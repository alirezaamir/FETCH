import os

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import random
import warnings

# Filter out the specific UserWarning related to torchvision
warnings.filterwarnings("ignore", category=UserWarning, message="Failed to load image Python extension")
# TODO solve the CUDA version issue

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import roc_auc_score
from torch.optim.lr_scheduler import StepLR
from tqdm import tqdm

import tuh_dataset
from vit_pytorch.vit import ViT
import torch.multiprocessing
torch.multiprocessing.set_sharing_strategy('file_system')

print(f"Torch: {torch.__version__}")

PATIENCE_EARLY_STOPPING = 10
VAL_EVERY = 1
EPOCHS = 50
GENERAL_MODEL = False


def seed_everything(seed=99):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True


seed_everything()

device = 'cuda'
# model = ViT(image_size=(3200, 15), patch_size=(80, 5), num_classes=1, dim=16, depth=4, heads=4, mlp_dim=4, pool='cls',
#             channels=1, dim_head=4, dropout=0.2, emb_dropout=0.2).to(device)
root_path = '/home/amirshah/EPFL/EpilepsyTransformer/TUSZv2/preprocess'
# model_path = os.path.join(root_path, 'pretrain_full_channel/model_12_0.9333263693136304')
model_path = os.path.join(root_path, 'test_STFT8/model_17_0.9159300189983679')
model = torch.load(model_path,  map_location=torch.device(device))
sigmoid = nn.Sigmoid()

# Training settings
batch_size = 1024
lr = 3e-5
gamma = 0.25
tuh_dataset.args.eeg_type = 'stft'

# loss function
criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([16]).to(device))
# optimizer
optimizer = optim.Adam(model.parameters(), lr=lr)
# scheduler
scheduler = StepLR(optimizer, step_size=10, gamma=gamma)

train_loader, val_loader, test_loader = tuh_dataset.get_data_loader(batch_size, remove_not_used=False, masking=True,
                                                                    balanced_data=False)

best_val_auc = 0.0
best_val_epoch = 0
model_directory = os.path.join(tuh_dataset.args.save_directory,
                               'test_8ch_{}'.format(tuh_dataset.args.selected_channel_id))
# model_directory = os.path.join(tuh_dataset.args.save_directory,
#                                'pretrain_full_channel')
if not os.path.exists(model_directory):
    os.mkdir(model_directory)

for epoch in range(EPOCHS):

    model.train()
    train_label_all = []
    train_prob_all = []
    epoch_train_loss = 0
    for data, label in tqdm(train_loader, desc='Training '):
        train_label_all.extend(label)

        data = data.to(device)
        label = label.to(device).float()

        prob = model(data)
        prob = torch.squeeze(prob)
        train_prob_all.extend(prob.cpu().detach().numpy())

        loss = criterion(prob, label)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        epoch_train_loss += loss / len(train_loader)

    train_auc = roc_auc_score(train_label_all, train_prob_all)

    if epoch % VAL_EVERY != VAL_EVERY-1:
        continue

    model.eval()
    val_label_all = []
    val_prob_all = []
    epoch_val_loss = 0
    with torch.no_grad():
        for data, label in tqdm(val_loader, desc='Evaluation '):
            val_label_all.extend(label)

            data = data.to(device)
            label = label.to(device).float()

            val_prob = model(data)
            val_prob_sigmoid = torch.squeeze(sigmoid(val_prob))
            val_prob_all.extend(val_prob_sigmoid.cpu().numpy())

            val_loss = criterion(torch.squeeze(val_prob), label)

            epoch_val_loss += val_loss / len(val_loader)

    val_auc = roc_auc_score(val_label_all, val_prob_all)

    print(f"Epoch: {epoch + 1} - train_loss: {epoch_train_loss:.4f} -  train_auc: {train_auc:.4f}; "
          f"val_loss: {epoch_val_loss:.4f} - val_auc: {val_auc:.4f}")

    if best_val_auc < val_auc:
        best_val_auc = val_auc
        best_val_epoch = epoch
        torch.save(model, os.path.join(model_directory, 'model_{}_{}'.format(epoch, val_auc)))

        if not GENERAL_MODEL:
            model.eval()
            test_label_all = []
            test_prob_all = []
            epoch_test_loss = 0
            with torch.no_grad():
                for data, label in tqdm(test_loader, desc='Testing '):
                    test_label_all.extend(label)

                    data = data.to(device)
                    label = label.to(device).float()

                    test_prob = model(data)
                    test_prob_sigmoid = torch.squeeze(sigmoid(test_prob))
                    test_prob_all.extend(test_prob_sigmoid.cpu().numpy())

                    test_loss = criterion(torch.squeeze(test_prob), label)

                    epoch_test_loss += test_loss / len(test_loader)

            test_auc = roc_auc_score(test_label_all, test_prob_all)
            print(f"test_loss: {epoch_test_loss:.4f} - test_auc: {test_auc:.4f}")

    if epoch > best_val_epoch + PATIENCE_EARLY_STOPPING:
        torch.save(model, os.path.join(model_directory, 'test_model_last_{}'.format(epoch)))
        break
