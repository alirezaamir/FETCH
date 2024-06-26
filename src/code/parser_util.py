# coding=utf-8
import os
import argparse


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-root', '--dataset_root',
                        type=str,
                        help='path to dataset',
                        default='..' + os.sep + 'dataset')

    parser.add_argument('-exp', '--experiment_root',
                        type=str,
                        help='root where to store models, losses and accuracies',
                        default='../output' + os.sep + 'output3')

    parser.add_argument('-data_root', '--data_root',
                        type=str,
                        help='root where the input data is stored',
                        default='/home/amirshah/EPFL/EpilepsyTransformer/TUSZv2/preprocess')

    parser.add_argument('-nep', '--epochs',
                        type=int,
                        help='number of epochs to train for',
                        default=500)

    parser.add_argument('-lr', '--learning_rate',
                        type=float,
                        help='learning rate for the model, default=0.001',
                        default=0.001)

    parser.add_argument('-lrS', '--lr_scheduler_step',
                        type=int,
                        help='StepLR learning rate scheduler step, default=20',
                        default=20)

    parser.add_argument('-lrG', '--lr_scheduler_gamma',
                        type=float,
                        help='StepLR learning rate scheduler gamma, default=0.5',
                        default=0.5)

    parser.add_argument('-its', '--iterations',
                        type=int,
                        help='number of episodes per epoch, default=100',
                        default=200)

    parser.add_argument('-cTr', '--classes_per_it_tr',
                        type=int,
                        help='number of random classes per episode for training, default=60',
                        default=2)

    parser.add_argument('-nsTr', '--num_support_tr',
                        type=int,
                        help='number of samples per class to use as support for training, default=5',
                        default=25)

    parser.add_argument('-nqTr', '--num_query_tr',
                        type=int,
                        help='number of samples per class to use as query for training, default=5',
                        default=25)

    parser.add_argument('-cVa', '--classes_per_it_val',
                        type=int,
                        help='number of random classes per episode for validation, default=5',
                        default=2)

    parser.add_argument('-nsVa', '--num_support_val',
                        type=int,
                        help='number of samples per class to use as support for validation, default=5',
                        default=25)

    parser.add_argument('-nqVa', '--num_query_val',
                        type=int,
                        help='number of samples per class to use as query for validation, default=15',
                        default=25)

    parser.add_argument('-seed', '--manual_seed',
                        type=int,
                        help='input for the manual seeds initializations',
                        default=7)

    parser.add_argument('--cuda',
                        action='store_false',
                        help='enables cuda')

    parser.add_argument('--sample_rate', type=int, default=256)
    parser.add_argument('--data_directory', type=str, default='/home/amirshah/EPFL/TUSZv2')
    parser.add_argument('--save_directory', type=str,
                        default='/home/amirshah/EPFL/EpilepsyTransformer/TUSZv2/preprocess')
    parser.add_argument('--label_type', type=str, default='csv_bi')
    parser.add_argument('--cpu_num', type=int, default=32)
    parser.add_argument('--data_type', type=str, default='eval', choices=['train', 'eval', 'dev'])
    parser.add_argument('--task_type', type=str, default='binary', choices=['binary'])
    parser.add_argument('--slice_length', type=int, default=12)
    parser.add_argument('--eeg_type', type=str, default='stft', choices=['original', 'bipolar', 'stft'])
    parser.add_argument('--selected_channel_id', type=int, default=-1)
    parser.add_argument('--global_model', action='store_true', help='enables global model')
    parser.add_argument('--server', action='store_true', help='enables server mode -> use more memory')
    parser.add_argument('--num_nodes', type=int, default=-1, help="number of nodes in EEG")

    return parser
