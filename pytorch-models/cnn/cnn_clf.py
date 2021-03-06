import torch
import numpy as np


class CNNClassifier(torch.nn.Module):
    def __init__(self, img_size, img_ch, kernel_size, pool_size, n_out):
        super(CNNClassifier, self).__init__()
        self.img_size = img_size
        self.img_ch = img_ch
        self.kernel_size = kernel_size
        self.pool_size = pool_size
        self.n_out = n_out
        self.build_model()
    # end constructor


    def build_model(self):
        self.conv1 = torch.nn.Sequential(
            torch.nn.Conv2d(self.img_ch, 16, kernel_size=self.kernel_size, padding=2),
            torch.nn.BatchNorm2d(16),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(self.pool_size))
        self.conv2 = torch.nn.Sequential(
            torch.nn.Conv2d(16, 32, kernel_size=self.kernel_size, padding=2),
            torch.nn.BatchNorm2d(32),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(self.pool_size))
        self.fc = torch.nn.Linear(int(self.img_size[0]/4)*int(self.img_size[1]/4)*32, self.n_out)
        self.criterion = torch.nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
    # end method build_model


    def forward(self, X):
        conv1_out = self.conv1(X)
        conv2_out = self.conv2(conv1_out)
        fully_connected = self.shrink(conv2_out)
        logits = self.fc(fully_connected)
        return logits
    # end method forward


    def shrink(self, X):
        return X.view(X.size(0), -1)
    # end method flatten


    def fit(self, X, y, num_epochs, batch_size):
        for epoch in range(num_epochs):
            for i, (X_batch, y_batch) in enumerate(zip(self.gen_batch(X, batch_size),
                                                       self.gen_batch(y, batch_size))):
                inputs = torch.autograd.Variable(torch.from_numpy(X_batch.astype(np.float32)))
                labels = torch.autograd.Variable(torch.from_numpy(y_batch.astype(np.int64)))

                preds = self.forward(inputs)            # cnn output
                loss = self.criterion(preds, labels)    # cross entropy loss
                self.optimizer.zero_grad()              # clear gradients for this training step
                loss.backward()                         # backpropagation, compute gradients
                self.optimizer.step()                   # apply gradients
                preds = torch.max(preds, 1)[1].data.numpy().squeeze()
                acc = (preds == y_batch).mean()
                if (i+1) % 100 == 0:
                    print ('Epoch [%d/%d], Step [%d/%d], Loss: %.4f, Acc: %.4f'
                           %(epoch+1, num_epochs, i+1, int(len(X)/batch_size), loss.data[0], acc))
    # end method fit


    def evaluate(self, X_test, y_test, batch_size):
        correct = 0
        total = 0
        for X_batch, y_batch in zip(self.gen_batch(X_test, batch_size),
                                              self.gen_batch(y_test, batch_size)):
            inputs = torch.autograd.Variable(torch.from_numpy(X_batch.astype(np.float32)))
            labels = torch.from_numpy(y_batch.astype(np.int64))
            preds = self.forward(inputs)
            _, preds = torch.max(preds.data, 1)
            total += labels.size(0)
            correct += (preds == labels).sum()
        print('Test Accuracy of the model on the 10000 test images: %d %%' % (100 * correct / total)) 
    # end method evaluate


    def gen_batch(self, arr, batch_size):
        for i in range(0, len(arr), batch_size):
            yield arr[i : i + batch_size]
    # end method gen_batch
# end class CNNClassifier
