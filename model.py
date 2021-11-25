import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os 


class LinearQNet(nn.Module):
  def __init__(self, input_size, hidden_size, output_size):
    super().__init__()
    self.linear1 = nn.Linear(input_size, hidden_size)
    self.linear2 = nn.Linear(hidden_size, output_size)

  def forward(self, x):
    x = F.relu(self.linear1(x))
    x = self.linear2(x)
    return x

  def save(self, filename='model.pth'):
    model_folder_path = "./model"
    if not os.path.exists(model_folder_path):
      os.makedirs(model_folder_path)
    filename = os.path.join(model_folder_path, filename)
    torch.save(self.state_dict(), filename)

  def load(self, file_path='./model/model.pth'):
    self.load_state_dict(torch.load(file_path))

class QTrainer:
  def __init__(self, model, lr, gamma):
    self.lr = lr
    self.model = model
    self.gamma = gamma
    self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
    self.loss = nn.MSELoss()

  def train_step(self, state, action, reward, next_state, done):
    state = torch.tensor(state, dtype=torch.float)
    next_state = torch.tensor(next_state, dtype=torch.float)
    action = torch.tensor(action, dtype=torch.long)
    reward = torch.tensor(reward, dtype=torch.float)
    # if multiple batches the dimension is (n_batches, x)
    # handle single batch
    if len(state.shape) == 1:
      # (1, x)
      state = torch.unsqueeze(state, 0)
      next_state = torch.unsqueeze(next_state, 0)
      action = torch.unsqueeze(action, 0)
      reward = torch.unsqueeze(reward, 0)
      done = (done, )
    # predicted Q value with the current state
    pred_Q = self.model(state)
    # Q_new = R + gamma * max(nex_predicted_Q)
    # pred_Q is an array e.g. [1,0,0] but ...
    target = pred_Q.clone()
    for idx in range(len(done)):
      Q_new = reward[idx]
      if not done[idx]:
        Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
      target[idx][torch.argmax(action[idx]).item()] = Q_new
    self.optimizer.zero_grad()
    loss = self.loss(target, pred_Q)
    loss.backward()
    self.optimizer.step()
