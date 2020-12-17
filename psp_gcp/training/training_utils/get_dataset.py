###Downloading the training and test datasets and uploading them to a GCP Storage Bucket
#Datasets downloaded to local psp_gcp directory as they are required when the GCP job is packaged
#and sent to GCP Ai-Platform

#importing libraries and dependancies
import numpy as np
import gzip
import h5py
import os
import requests
import shutil
import argparse
import training.training_utils.gcp_utils as utils
from training.training_utils.globals import *

class CulPDB6133(object):

    def __init__(self, all_data =1, filtered = True):

        self.all_data = all_data
        self.filtered = filtered

        print("Loading training dataset (Cullpdb_filtered)...\n")

        if (self.filtered):
            self.train_path = TRAIN_PATH_FILTERED_NPY
        else:
            self.train_path = TRAIN_PATH_UNFILTERED_NPY

        #download dataset if not already in current directory
        # if not (os.path.isfile(os.getcwd() + '/data/' + self.train_path)):
        if not (os.path.isfile(os.path.join(os.getcwd(), 'data', self.train_path))):
            # get_cullpdb_filtered()
            print("getting dataset now...")
            self.get_cullpdb(self.filtered)

        #load dataset
        # data = np.load(self.train_path)
        data = np.load(os.path.join(os.getcwd(), 'data', self.train_path))

        #reshape dataset
        data = np.reshape(data, (-1, 700, 57))
        #sequence feature
        datahot = data[:, :, 0:21]
        #profile features
        datapssm = data[:, :, 35:56]
        #secondary struture labels
        labels = data[:, :, 22:30]

        # shuffle data
        num_seqs, seqlen, feature_dim = np.shape(data)
        num_classes = labels.shape[2]
        seq_index = np.arange(0, num_seqs)#
        np.random.shuffle(seq_index)

        #calculate the indexes for each dimension based on all_data input parameter
        data_index = int(5278 * all_data)
        val_data_index =  int(256 * all_data)
        val_data_upper = data_index + val_data_index

        #get training data
        trainhot = datahot[seq_index[:data_index]]
        trainlabel = labels[seq_index[:data_index]]
        trainpssm = datapssm[seq_index[:data_index]]

        #get validation data
        vallabel = labels[seq_index[data_index:val_data_upper]] #8
        valpssm = datapssm[seq_index[data_index:val_data_upper]] # 21
        valhot = datahot[seq_index[data_index:val_data_upper]] #21


        train_hot = np.ones((trainhot.shape[0], trainhot.shape[1]))
        for i in range(trainhot.shape[0]):
            for j in range(trainhot.shape[1]):
                if np.sum(trainhot[i,j,:]) != 0:
                    train_hot[i,j] = np.argmax(trainhot[i,j,:])


        val_hot = np.ones((valhot.shape[0], valhot.shape[1]))
        for i in range(valhot.shape[0]):
            for j in range(valhot.shape[1]):
                if np.sum(valhot[i,j,:]) != 0:
                    val_hot[i,j] = np.argmax(valhot[i,j,:])

        #delete training data from ram
        del data

        self.train_hot = train_hot
        self.trainpssm = trainpssm
        self.trainlabel = trainlabel
        self. val_hot = val_hot
        self.valpssm = valpssm
        self.vallabel = vallabel

    def get_cullpdb(self, filtered):

        if not (os.path.isdir('data')):
            os.makedirs('data')

        if (filtered):
            train_path = TRAIN_PATH_FILTERED
            train_url = TRAIN_FILTERED_URL
        else:
            train_path = TRAIN_PATH_UNFILTERED
            train_url = TRAIN_UNFILTERED_URL

        try:
            if not (os.path.isfile(os.path.join(os.getcwd(), 'data', train_path))):

                r = requests.get(train_url, allow_redirects = True) #error handling, if response == 200
                r.raise_for_status()

                dir_path = (os.path.join(os.getcwd(), 'data'))
                source_path = (os.path.join(dir_path, train_path))
                destination_path = os.path.join(dir_path, train_path[:-3])

                open(source_path, 'wb').write(r.content)

                print('Exporting Cullpdb 6133 datatset....')
                with gzip.open(source_path, 'rb') as f_in:
                    with open(destination_path, 'wb') as f_out:
                        shutil.copyfile(source_path, destination_path)

                os.remove(os.path.join(os.getcwd(), 'data', train_path))

            else:
                #dataset already present
                print(str(self) + " already present...")

        except OSError:
            print('Error downloading and exporting training dataset\n')

    #get length of CullPDB training dataset
    def __len__(self):
        return (self.train_hot[:,0].shape[0])

    def __str__(self):
        return ('CullPDB6133 Training datatset - filtered: {}'.format(self.filtered))

    def is_filtered(self):
        return self.filtered

    def shape(self):
        return self.train_hot.shape

    def get_data_labels(self, protein_index):

        labels = self.trainlabel[protein_index,:,:]

        return labels


class CB513(object):

    def __init__(self):

        print("Loading test dataset (CB513)...\n")

        #download dataset if not already in current directory
        # if not (os.path.isfile(TEST_PATH)):
        if not (os.path.isfile(os.path.join(os.getcwd(), 'data', CB513_NPY))):
            self.get_cb513()

        #load test dataset
        CB513 = np.load(os.path.join(os.getcwd(), 'data', CB513_NPY))

        #reshape dataset
        CB513= np.reshape(CB513,(-1,700,57))
        #sequence feature
        testhot=CB513[:, :, 0:21]
        #profile feature
        testpssm=CB513[:, :, 35:56]
        #secondary struture label
        testlabel = CB513[:, :, 22:30]

        testhot = testhot[:514]
        testpssm = testpssm[:514]
        testlabel = testlabel[:514]

        #convert to one-hot array
        test_hot = np.ones((testhot.shape[0], testhot.shape[1]))
        for i in range(testhot.shape[0]):
            for j in range(testhot.shape[1]):
                if np.sum(testhot[i,j,:]) != 0:
                    test_hot[i,j] = np.argmax(testhot[i,j,:])

        #delete test data from ram
        del CB513

        self.test_hot = test_hot
        self.testpssm = testpssm
        self.testlabel = testlabel

    def get_cb513(self):

        if not (os.path.isdir('data')):
            os.makedirs('data')

        try:
            if not (os.path.isfile(os.path.join(os.getcwd(), 'data', CB513_PATH))):

                r = requests.get(CB513_URL, allow_redirects = True) #error handling, if response == 200
                r.raise_for_status()

                dir_path = (os.path.join(os.getcwd(), 'data'))
                source_path = (os.path.join(dir_path, CB513_PATH))
                destination_path = os.path.join(dir_path, CB513_PATH[:-3])

                open(source_path, 'wb').write(r.content)

                print('Exporting CB513 datatset....')
                with gzip.open(source_path, 'rb') as f_in:
                    with open(destination_path, 'wb') as f_out:
                        shutil.copyfile(source_path, destination_path)

                os.remove(os.path.join(os.getcwd(), 'data', CB513_PATH))

            else:
                #dataset already present
                print(str(self) + " already present...")

        except OSError:
            print('Error downloading and exporting dataset\n')

    def __len__(self):
        return (self.test_hot[:,0].shape[0])

    def __str__(self):
        return ('CB513 Test datatset')

    def shape(self):
        return self.test_hot.shape

    def get_data_labels(self, protein_index):

        labels = self.testlabel[protein_index,:,:]

        return labels


class CASP10(object):


    def __init__(self):

        print("Loading CASP10 dataset...\n")

        #download dataset if not already in current directory
        # if not (os.path.isfile(CASP10_PATH)):
        if not (os.path.isfile(os.path.join(os.getcwd(), 'data', CASP10_PATH))):
            self.get_casp10()

        #load casp10 dataset
        # casp10_data = h5py.File(CASP10_PATH, 'r')
        casp10_data = h5py.File((os.path.join(os.getcwd(), 'data', CASP10_PATH)),'r')

        #load protein sequence and profile feature data
        casp10_data_hot = casp10_data['features'][:, :, 0:21]
        casp10_data_pssm = casp10_data['features'][:, :, 21:42]

        #load protein label data
        test_labels = casp10_data['labels'][:, :, 0:8]

        #create new protein sequence feature, set values to max value if if value!=0 ?
        casp10_data_test_hot = np.ones((casp10_data_hot.shape[0], casp10_data_hot.shape[1]))
        for x in range(casp10_data_hot.shape[0]):
            for y in range(casp10_data_hot.shape[1]):
                   if np.sum(casp10_data_hot[x,y,:]) != 0:
                        casp10_data_test_hot[x,y] = np.argmax(casp10_data_hot[x,y,:])

        print('CASP10 dataset loaded...\n')

        #delete test data from ram
        del casp10_data

        self.casp10_data_test_hot = casp10_data_test_hot
        self.casp10_data_pssm = casp10_data_pssm
        self.test_labels = test_labels


    def get_casp10(self):

        if not (os.path.isdir('data')):
            os.makedirs('data')

        try:
            if not (os.path.isfile(os.path.join(os.getcwd(), 'data', CASP10_PATH))):

                r = requests.get(CASP10_URL, allow_redirects = True) #error handling, if response == 200
                r.raise_for_status()

                dir_path = (os.path.join(os.getcwd(), 'data'))
                source_path = (os.path.join(dir_path, CASP10_PATH))
                destination_path = os.path.join(dir_path, CASP10_PATH[:-3])

                open(source_path, 'wb').write(r.content)

                print('Exporting CASP10 datatset....')
                with gzip.open(source_path, 'rb') as f_in:
                    with open(destination_path, 'wb') as f_out:
                        shutil.copyfile(source_path, destination_path)
            else:
                #dataset already present
                print(str(self) + " already present...")

        except OSError:
            print('Error downloading and exporting dataset\n')



    def __len__(self):
        return (self.casp10_data_test_hot[:,0].shape[0])

    def __str__(self):
        return ('CASP10 Test datatset')

    def shape(self):
        return self.casp10_data_test_hot.shape

    def get_data_labels(self, protein_index):

        labels = self.test_labels[protein_index,:,:]

        return labels


'''
CASP11 Test Dataset class 
'''
class CASP11(object):


    def __init__(self):

        print("Loading CASP11 dataset...\n")


        #download dataset if not already in current directory
        # if not (os.path.isfile(CASP11_PATH)):
        if not (os.path.isfile(os.path.join(os.getcwd(), 'data', CASP11_PATH))):
            self.get_casp11()

        #load casp11 dataset
        # casp11_data = h5py.File(CASP11_PATH, 'r')
        casp11_data = h5py.File((os.path.join(os.getcwd(), 'data', CASP11_PATH)),'r')

        #load protein sequence and profile feature data
        casp11_data_hot = casp11_data['features'][:,:,0:21]
        casp11_data_pssm = casp11_data['features'][:,:,21:42]
        #load protein label data
        test_labels = casp11_data['labels'][:,:,0:8]

        #create new protein sequence feature, set values to max value if if value!=0 ?
        casp11_data_test_hot = np.ones((casp11_data_hot.shape[0], casp11_data_hot.shape[1]))
        for x in range(casp11_data_hot.shape[0]):
            for y in range(casp11_data_hot.shape[1]):
                if np.sum(casp11_data_hot[x,y,:]) != 0:
                    casp11_data_test_hot[x,y] = np.argmax(casp11_data_hot[x,y,:])

        print('CASP11 dataset loaded...\n')

        #delete test data from ram
        del casp11_data

        self.casp11_data_test_hot = casp11_data_test_hot
        self.casp11_data_pssm = casp11_data_pssm
        self.test_labels = test_labels

    def get_casp11(self):

        if not (os.path.isdir('data')):
            os.makedirs('data')

        try:
            if not (os.path.isfile(os.path.join(os.getcwd(), 'data', CASP11_PATH))):

                r = requests.get(CASP11_URL, allow_redirects = True) #error handling, if response == 200
                r.raise_for_status()

                dir_path = (os.path.join(os.getcwd(), 'data'))
                source_path = (os.path.join(dir_path, CASP11_PATH))
                destination_path = os.path.join(dir_path, CASP11_PATH[:-3])

                open(source_path, 'wb').write(r.content)

                print('Exporting CASP11 datatset....')
                with gzip.open(source_path, 'rb') as f_in:
                    with open(destination_path, 'wb') as f_out:
                        shutil.copyfile(source_path, destination_path)
            else:
                #dataset already present
                print(str(self) + " already present...")

        except OSError:
            print('Error downloading and exporting dataset\n')


    def __len__(self):
        return (self.casp11_data_test_hot[:,0].shape[0])

    def __str__(self):
        return ('CASP11 Test datatset')

    def shape(self):
        return self.casp11_data_test_hot.shape

    def get_data_labels(self, protein_index):

        labels = self.test_labels[protein_index,:,:]

        return labels

if __name__ == "main":

    #initialise input arguments
    parser = argparse.ArgumentParser(description='Loading training and test datasets')

    parser.add_argument('-all_data', '--all_data', required = False, default = 1.0,
                    help='Determine what proportion of dataset to load')

    #parse arguments
    args = parser.parse_args()
