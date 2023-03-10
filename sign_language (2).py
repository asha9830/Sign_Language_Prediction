# -*- coding: utf-8 -*-
"""Sign_Language.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SFJFPSZuyE3y2SOHys-F2tFFTikW9Pw-

**Importing Libraries**
"""

# Commented out IPython magic to ensure Python compatibility.
import os
import torch
import torchvision
import tarfile
import torch.nn as nn
import numpy as np
import torch.nn.functional as F
from torchvision.datasets.utils import download_url
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader, SubsetRandomSampler
import torchvision.transforms as tt
from torch.utils.data import random_split
from torchvision.utils import make_grid
import matplotlib
import matplotlib.pyplot as plt
# import opendatasets as od
# %matplotlib inline

matplotlib.rcParams['figure.facecolor'] = '#ffffff'

"""**Project Name**"""

Project_Name='Indian_Sign_Language'

"""**Mounting google drive**"""

from google.colab import drive

drive.mount('/content/gdrive/', force_remount=True)

# Look into the data directory
# Change the directory as required
Data_Directory = '/content/gdrive/MyDrive/Sign_Language/data/'
Classes_Found = os.listdir(Data_Directory)
print(Classes_Found)

# Let's evaluate a single class say "A"
A_File = os.listdir(Data_Directory+"A")
print("NO. of Training examples for Man:",len(A_File))
print(A_File[:5])

# Let's evaluate a single class say "9"
Num_9_File = os.listdir(Data_Directory+"9")
print("NO. of Training examples for Man:",len(Num_9_File))
print(Num_9_File[:5])

DataSets={}
for i in Classes_Found:
    DataSets[i]=len(os.listdir(Data_Directory+i))
print(DataSets)

Target_num = len(Classes_Found)
Target_num

# THe below function will print a batch of 64 images from the dataset
def show_batch(Data1):
    for Images, Labels in Data1:
        Fig, Ax = plt.subplots(figsize=(12, 12))
        Ax.set_xticks([]); Ax.set_yticks([])
        Ax.imshow(make_grid(Images[:64], nrow=8).permute(1, 2, 0))
        break

Raw_Images = ImageFolder(Data_Directory, tt.ToTensor())

Image, Label = Raw_Images[0]
print("Dimension:", Image.shape)
plt.imshow(Image.permute(1, 2, 0))

# Let's create a dataloader for raw images
Raw_Data_1 = DataLoader(Raw_Images, 400, shuffle=True, num_workers=2, pin_memory=True)
show_batch(Raw_Data_1)

Average  = torch.Tensor([0,0,0])
Standard_Deviation = torch.Tensor([0,0,0])

for Image, Labels in Raw_Images:
    Average += Image.mean([1,2])
    Standard_Deviation += Image.std([1,2])
Stats_Avgs = (Average / len(Raw_Images)).tolist()
Stats_Stds =  (Standard_Deviation / len(Raw_Images)).tolist()
Stats_Avgs, Stats_Stds

# Data transforms (normalization & data augmentation)
Stats = (Stats_Avgs, Stats_Stds)
Train_Transform = tt.Compose([
                         tt.RandomHorizontalFlip(), 
                         tt.ToTensor(), 
                         tt.Normalize(*Stats,inplace=True)])
Valid_Transform = tt.Compose([tt.ToTensor(), tt.Normalize(*Stats)])

rain_DataSet = ImageFolder(Data_Directory, transform=Train_Transform)
Validate_DataSet = ImageFolder(Data_Directory, transform=Valid_Transform)
Test_DataSet = ImageFolder(Data_Directory, transform=Valid_Transform)

Length_Of_Train_data = len(Train_DataSet)
Indices_of_Dataset = list(range(Length_Of_Train_data))

np.random.seed(42) 
np.random.shuffle(Indices_of_Dataset)

# Let's take 15% of the train data as validation and 10% as test
Validate_Size = 0.15
Test_Data_Size = 0.10
Validate_Split = int(np.floor(Validate_Size * Length_Of_Train_data))
Test_Data_Split = int(np.floor(Test_Data_Size * Length_Of_Train_data))
Validate_Index, Test_Data_Index, Train_Data_Index = Indices_of_Dataset[:Validate_Split], Indices_of_Dataset[Validate_Split:Validate_Split+Test_Data_Split], Indices_of_Dataset[Validate_Split+Test_Data_Split:]

Batch_Size_of_Dataset = 250

# define samplers for obtaining training and validation batches
Train_Data_Sampler = SubsetRandomSampler(Train_Data_Index)
Validate_Data_Sampler = SubsetRandomSampler(Validate_Index)

# prepare data loaders 
Train_DataSet_1 = torch.utils.data.DataLoader(Train_DataSet, batch_size=Batch_Size_of_Dataset, 
    sampler=Train_Data_Sampler, num_workers=2, pin_memory=True)
Validate_Dataset_1 = torch.utils.data.DataLoader(Validate_DataSet, batch_size=Batch_Size_of_Dataset,
    sampler=Validate_Data_Sampler, num_workers=2, pin_memory=True)

# Let's remove the unwanted variables from memory
del Raw_Images, Average, Standard_Deviation, Raw_Data_1

def denormalize(Images, Means, Stand_Dev):
    Means = torch.tensor(Means).reshape(1, 3, 1, 1)
    Stand_Dev = torch.tensor(Stand_Dev).reshape(1, 3, 1, 1)
    return Images * Stand_Dev + Means

def show_batch(Dataset_1, denorm=False):
    for Images, Labels in Dataset_1:
        Figure, Axis = plt.subplots(figsize=(12, 12))
        Axis.set_xticks([]); Axis.set_yticks([])
        if denorm:
            Images = denormalize(Images, *Stats)
        Axis.imshow(make_grid(Images[:64], nrow=8).permute(1, 2, 0).clamp(0,1))
        break

# Normalized and Augmented Image
show_batch(Train_DataSet_1)

# Original Image
show_batch(Train_DataSet_1, denorm=True)

show_batch(Validate_Dataset_1)

def get_default_device():
    """Pick GPU if available, else CPU"""
    if torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')
    
def to_device(data, device):
    """Move tensor(s) to chosen device"""
    if isinstance(data, (list,tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)

class DeviceDataLoader():
    """Wrap a dataloader to move data to a device"""
    def __init__(self, dl, device):
        self.dl = dl
        self.device = device
        
    def __iter__(self):
        """Yield a batch of data after moving it to device"""
        for b in self.dl: 
            yield to_device(b, self.device)

    def __len__(self):
        """Number of batches"""
        return len(self.dl)

device = get_default_device()
device

Train_DataSet_1 = DeviceDataLoader(Train_DataSet_1, device)
Validate_Dataset_1 = DeviceDataLoader(Validate_Dataset_1, device)

def accuracy(Outputs, Labels):
    _, Pedicts_Data = torch.max(Outputs, dim=1)
    return torch.tensor(torch.sum(Pedicts_Data == Labels).item() / len(Pedicts_Data))

class ImageClassificationBase(nn.Module):
    def training_step(self, Bacth_Data):
        Images, Labels = Bacth_Data 
        Out = self(Images)                  # Generate predictions
        Loss = F.cross_entropy(Out, Labels) # Calculate loss
        return Loss
    
    def validation_step(self, Bacth_Data):
        Images, Labels = Bacth_Data 
        Out = self(Images)                    # Generate predictions
        Loss = F.cross_entropy(Out, Labels)   # Calculate loss
        Acc = accuracy(Out, Labels)           # Calculate accuracy
        return {'val_loss': Loss.detach(), 'val_acc': Acc}
        
    def validation_epoch_end(self, outputs):
        Batch_losses_Found = [x['val_loss'] for x in outputs]
        Epoch_loss_Found = torch.stack(Batch_losses_Found).mean()   # Combine losses
        Batch_accuracy_Found = [x['val_acc'] for x in outputs]
        Epoch_accuracy_Found = torch.stack(Batch_accuracy_Found).mean()      # Combine accuracies
        return {'val_loss': Epoch_loss_Found.item(), 'val_acc': Epoch_accuracy_Found.item()}
    
    def epoch_end(self, epoch, result):
        print("Epoch [{}], last_lr: {:.5f}, train_loss: {:.4f}, val_loss: {:.4f}, val_acc: {:.4f}".format(
            epoch, result['lrs'][-1], result['train_loss'], result['val_loss'], result['val_acc']))

def conv_block(in_channels, out_channels, pool=False):
    Layers_of_CNN = [nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1), 
              nn.BatchNorm2d(out_channels), 
              nn.ReLU(inplace=True)]
    if pool: Layers_of_CNN.append(nn.MaxPool2d(2))
    return nn.Sequential(*Layers_of_CNN)

class ResNet9(ImageClassificationBase):
    def __init__(self, in_channels, num_classes):
        super().__init__()
        
        self.Cov_Net_1 = conv_block(in_channels, 64, pool=True) # 64 x 64 x 64
        self.Cov_Net_2 = conv_block(64, 128, pool=True) # 128 x 32 x 32
        self.Res_Net_1 = nn.Sequential(conv_block(128, 128), conv_block(128, 128)) # 128 x 32 x 32
        
        self.Cov_Net_3 = conv_block(128, 256, pool=True) # 256 x 16 x 16
        self.Cov_Net_4 = conv_block(256, 512, pool=True) # 512 x 8 x 8
        self.Res_Net_2 = nn.Sequential(conv_block(512, 512), conv_block(512, 512)) # 512 x 8 x 8
        self.Cov_Net_5 = conv_block(512, 512, pool=True) # 512 x 4 x 4
        
        self.classifier = nn.Sequential(nn.MaxPool2d(4), 
                                        nn.Flatten(), 
                                        nn.Dropout(0.2),
                                        nn.Linear(512, num_classes))
        
    def forward(self, xb):
        out = self.Cov_Net_1(xb)
        out = self.Cov_Net_2(out)
        out = self.Res_Net_1(out) + out
        out = self.Cov_Net_3(out)
        out = self.Cov_Net_4(out)
        out = self.Res_Net_2(out) + out
        out = self.Cov_Net_5(out)
        out = self.classifier(out)
        return out

Model = to_device(ResNet9(3, Target_num), device)
Model

@torch.no_grad()
def evaluate(Model, val_loader):
    Model.eval()
    outputs = [Model.validation_step(batch) for batch in val_loader]
    return Model.validation_epoch_end(outputs)

def get_lr(optimizer):
    for param_group in optimizer.param_groups:
        return param_group['lr']

def fit_one_cycle(epochs, max_lr, Model, train_loader, val_loader, 
                  weight_decay=0, grad_clip=None, opt_func=torch.optim.SGD):
    torch.cuda.empty_cache()
    History = []
    
    # Set up cutom optimizer with weight decay
    optimizer = opt_func(Model.parameters(), max_lr, weight_decay=weight_decay)
    # Set up one-cycle learning rate scheduler
    sched = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr, epochs=epochs, 
                                                steps_per_epoch=len(train_loader))
    
    for epoch in range(epochs):
        # Training Phase 
        Model.train()
        train_losses = []
        lrs = []
        for batch in train_loader:
            loss = Model.training_step(batch)
            train_losses.append(loss)
            loss.backward()
            
            # Gradient clipping
            if grad_clip: 
                nn.utils.clip_grad_value_(Model.parameters(), grad_clip)
            
            optimizer.step()
            optimizer.zero_grad()
            
            # Record & update learning rate
            lrs.append(get_lr(optimizer))
            sched.step()
        
        # Validation phase
        result = evaluate(Model, val_loader)
        result['train_loss'] = torch.stack(train_losses).mean().item()
        result['lrs'] = lrs
        Model.epoch_end(epoch, result)
        History.append(result)
    return History

History = [evaluate(Model, Validate_Dataset_1)]
History

Epochs = 20
Maximum_learning_rate = 0.01
Gradient_Cliping = 0.1
Weight_Decay = 1e-4  # Regularization
Optimisation_Function = torch.optim.Adam

# Commented out IPython magic to ensure Python compatibility.
# %%time
# History += fit_one_cycle(Epochs, Maximum_learning_rate, Model, Train_DataSet_1, Validate_Dataset_1, 
#                              grad_clip=Gradient_Cliping, 
#                              weight_decay=Weight_Decay, 
#                              opt_func=Optimisation_Function)

def plot_accuracies(History):
    accuracies = [x['val_acc'] for x in History]
    plt.plot(accuracies, '-x')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('Accuracy vs. No. of epochs');

plot_accuracies(History)

def plot_losses(History):
    Train_Losess = [x.get('train_loss') for x in History]
    Val_Losses = [x['val_loss'] for x in History]
    plt.plot(Train_Losess, '-bx')
    plt.plot(Val_Losses, '-rx')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend(['Training', 'Validation'])
    plt.title('Loss vs. No. of epochs');

plot_losses(History)

def plot_lrs(History):
    lrs = np.concatenate([x.get('lrs', []) for x in History])
    plt.plot(lrs)
    plt.xlabel('Batch no.')
    plt.ylabel('Learning rate')
    plt.title('Learning Rate vs. Batch no.');
plot_lrs(History)

def predict_image(img, Model):
    # Convert to a batch of 1
    xb = to_device(img.unsqueeze(0), device)
    # Get predictions from model
    yb = Model(xb)
    # Pick index with highest probability
    _, preds  = torch.max(yb, dim=1)
    # Retrieve the class label
    return Train_DataSet.classes[preds[0].item()]

Correct_Data_Predicted = [] 
for i in Test_Data_Index:
    img, lab = Test_DataSet[i]
    xb = to_device(img.unsqueeze(0), device)
    yb = Model(xb)
    _, preds  = torch.max(yb, dim=1)
    Correct_Data_Predicted.append(preds[0].item() == lab)
print(f"Accuracy [Test Data]: {(sum(Correct_Data_Predicted)) / (len(Test_Data_Index)) * 100}")

n_rows, n_cols, i = 3, 5, 1
fig = plt.figure(figsize=(16,10))
for index in Test_Data_Index[:15]:
    img, label = Test_DataSet[index]
    ax = fig.add_subplot(n_rows, n_cols, i)
    ax.set_xticks([]); ax.set_yticks([])
    ax.imshow(img.permute(1, 2, 0).clamp(0,1))
    ax.set_title(f"Label: {Test_DataSet.classes[label]} , Predicted: {predict_image(img, Model)}")
    i+=1

img, label = Validate_DataSet[200]
plt.imshow(img.permute(1, 2, 0))
print('Label:', Validate_DataSet.classes[label], ', Predicted:', predict_image(img, Model))

torch.save(Model.state_dict(), 'ISN-2-custom-resnet.pth')
import joblib
filename = 'ISN-1-custom-resnet.sav'
joblib.dump(Model, filename)