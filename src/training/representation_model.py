import time

import torch
import torch.nn as nn
import torch.nn.functional as F


class TreeNode(object):
    def __init__(self, current_vec, parent):
        self.item = current_vec
        self.parent = parent
        self.children = []

    def get_parent(self):
        return self.parent

    def get_item(self):
        return self.item

    def get_children(self):
        return self.children

    def add_child(self, child):
        self.children.append(child)

class BinaryTreeComposer(nn.Module):
    """
  local lc, lh = nn.Identity()(), nn.Identity()()
  local rc, rh = nn.Identity()(), nn.Identity()()
  local new_gate = function()
    return nn.CAddTable(){
      nn.Linear(self.mem_dim, self.mem_dim)(lh),
      nn.Linear(self.mem_dim, self.mem_dim)(rh)
    }
  end

  local i = nn.Sigmoid()(new_gate())    -- input gate
  local lf = nn.Sigmoid()(new_gate())   -- left forget gate
  local rf = nn.Sigmoid()(new_gate())   -- right forget gate
  local update = nn.Tanh()(new_gate())  -- memory cell update vector
  local c = nn.CAddTable(){             -- memory cell
      nn.CMulTable(){i, update},
      nn.CMulTable(){lf, lc},
      nn.CMulTable(){rf, rc}
    }

  local h
  if self.gate_output then
    local o = nn.Sigmoid()(new_gate()) -- output gate
    h = nn.CMulTable(){o, nn.Tanh()(c)}
  else
    h = nn.Tanh()(c)
  end
  local composer = nn.gModule(
    {lc, lh, rc, rh},
    {c, h})
    """
    def __init__(self, in_dim, mem_dim):
        super(BinaryTreeComposer, self).__init__()
        self.in_dim = in_dim
        self.mem_dim = mem_dim

        def new_gate():
            lh = nn.Linear(self.mem_dim, self.mem_dim)
            rh = nn.Linear(self.mem_dim, self.mem_dim)
            return lh, rh
        def input_gate():
            input = nn.Linear(self.in_dim, self.mem_dim)
            return input

        self.ilh, self.irh = new_gate()
        self.lflh, self.lfrh = new_gate()
        self.rflh, self.rfrh = new_gate()
        self.ulh, self.urh = new_gate()
        self.olh, self.orh = new_gate()
        self.input = input_gate()

    def forward(self, input, lc, lh , rc, rh):
        i = F.sigmoid(self.input(input) + self.ilh(lh) + self.irh(rh))
        lf = F.sigmoid(self.input(input)+self.lflh(lh) + self.lfrh(rh))
        rf = F.sigmoid(self.input(input)+self.rflh(lh) + self.rfrh(rh))
        o = F.sigmoid(self.input(input)+self.olh(lh) + self.orh(rh))
        update = F.tanh(self.input(input)+self.ulh(lh) + self.urh(rh))
        c =  i* update + lf*lc + rf*rc
        h =o* F.tanh(c)
        return c, h

class Representation(nn.Module):
    def __init__(self, input_dim, hidden_dim, hid_dim, middle_result_dim, task_num):
        super(Representation, self).__init__()
        self.hidden_dim = hidden_dim
        self.lstm1 = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.batch_norm1 = nn.BatchNorm1d(hid_dim)
        # The linear layer that maps from hidden state space to tag space

        self.sample_mlp = nn.Linear(1000, hid_dim)
        self.condition_mlp = nn.Linear(hidden_dim, hid_dim)

        #         self.out_mlp1 = nn.Linear(hidden_dim, middle_result_dim)
        #         self.hid_mlp1 = nn.Linear(15+108+2*hid_dim, hid_dim)
        #         self.out_mlp1 = nn.Linear(hid_dim, middle_result_dim)

        # self.lstm2 = nn.LSTM(15 + 108 + 2 * hid_dim, hidden_dim, batch_first=True)
        self.lstm2 = nn.LSTM(15 + 7 + 2 + hid_dim, hidden_dim, batch_first=True)
        #         self.lstm2_binary = nn.LSTM(15+108+2*hid_dim, hidden_dim, batch_first=True)
        #         self.lstm2_binary = nn.LSTM(15+108+2*hid_dim, hidden_dim, batch_first=True)
        self.batch_norm2 = nn.BatchNorm1d(hidden_dim)
        # The linear layer that maps from hidden state space to tag space
        self.hid_mlp2_task1 = nn.Linear(hidden_dim, hid_dim)
        self.hid_mlp2_task2 = nn.Linear(hidden_dim, hid_dim)
        self.batch_norm3 = nn.BatchNorm1d(hid_dim)
        self.hid_mlp3_task1 = nn.Linear(hid_dim, hid_dim)
        self.hid_mlp3_task2 = nn.Linear(hid_dim, hid_dim)
        self.out_mlp2_task1 = nn.Linear(hid_dim, 1)
        self.out_mlp2_task2 = nn.Linear(hid_dim, 1)

    #         self.hidden2values2 = nn.Linear(hidden_dim, action_num)

    def init_hidden(self, hidden_dim, batch_size=1):
        # Before we've done anything, we dont have any hidden state.
        # Refer to the Pytorch documentation to see exactly
        # why they have this dimensionality.
        # The axes semantics are (num_layers, minibatch_size, hidden_dim)
        return (torch.zeros(1, batch_size, hidden_dim).cuda(),
                torch.zeros(1, batch_size, hidden_dim).cuda())

    def forward(self, operators, extra_infos, cardinalities, condition1s, condition2s, mapping):
        # condition1
        batch_size = 0
        for i in range(operators.size()[1]):
            if operators[0][i].sum(0) != 0:
                batch_size += 1
            else:
                break
        print('batch_size: ', batch_size)

        #         print (operators.size())
        #         print (extra_infos.size())
        #         print (condition1s.size())
        #         print (condition2s.size())
        #         print (samples.size())
        #         print (condition_masks.size())
        #         print (mapping.size())

        #         torch.Size([14, 133, 15])
        #         torch.Size([14, 133, 108])
        #         torch.Size([14, 133, 13, 1119])
        #         torch.Size([14, 133, 13, 1119])
        #         torch.Size([14, 133, 1000])
        #         torch.Size([14, 133, 1])
        #         torch.Size([14, 133, 2])

        num_level = condition1s.size()[0]
        num_node_per_level = condition1s.size()[1]
        num_condition_per_node = condition1s.size()[2]
        condition_op_length = condition1s.size()[3]

        inputs = condition1s.view(num_level * num_node_per_level, num_condition_per_node, condition_op_length)
        hidden = self.init_hidden(self.hidden_dim, num_level * num_node_per_level)

        out, hid = self.lstm1(inputs, hidden)
        last_output1 = hid[0].view(num_level * num_node_per_level, -1)

        # condition2
        num_level = condition2s.size()[0]
        num_node_per_level = condition2s.size()[1]
        num_condition_per_node = condition2s.size()[2]
        condition_op_length = condition2s.size()[3]

        inputs = condition2s.view(num_level * num_node_per_level, num_condition_per_node, condition_op_length)
        hidden = self.init_hidden(self.hidden_dim, num_level * num_node_per_level)

        out, hid = self.lstm1(inputs, hidden)
        last_output2 = hid[0].view(num_level * num_node_per_level, -1)

        last_output1 = F.relu(self.condition_mlp(last_output1))
        last_output2 = F.relu(self.condition_mlp(last_output2))
        last_output = (last_output1 + last_output2) / 2
        last_output = self.batch_norm1(last_output).view(num_level, num_node_per_level, -1)

        #         print (last_output.size())
        #         torch.Size([14, 133, 256])

        # sample_output = F.relu(self.sample_mlp(samples))
        # sample_output = sample_output * condition_masks

        out = torch.cat((operators, extra_infos, cardinalities, last_output), 2)
        #         print (out.size())
        #         torch.Size([14, 133, 635])
        #         out = out * node_masks
        start = time.time()
        hidden = self.init_hidden(self.hidden_dim, num_node_per_level)
        last_level = out[num_level - 1].view(num_node_per_level, 1, -1)
        #         torch.Size([133, 1, 635])
        _, (hid, cid) = self.lstm2(last_level, hidden)
        mapping = mapping.long()
        for idx in reversed(range(0, num_level - 1)):
            mapp_left = mapping[idx][:, 0]
            mapp_right = mapping[idx][:, 1]
            pad = torch.zeros_like(hid)[:, 0].unsqueeze(1)
            next_hid = torch.cat((pad, hid), 1)
            pad = torch.zeros_like(cid)[:, 0].unsqueeze(1)
            next_cid = torch.cat((pad, cid), 1)
            hid_left = torch.index_select(next_hid, 1, mapp_left)
            cid_left = torch.index_select(next_cid, 1, mapp_left)
            hid_right = torch.index_select(next_hid, 1, mapp_right)
            cid_right = torch.index_select(next_cid, 1, mapp_right)
            hid = (hid_left + hid_right) / 2
            cid = (cid_left + cid_right) / 2
            last_level = out[idx].view(num_node_per_level, 1, -1)
            _, (hid, cid) = self.lstm2(last_level, (hid, cid))
        output = hid[0]
        #         print (output.size())
        #         torch.Size([133, 128])
        end = time.time()
        print('Forest Evaluate Running Time: ', end - start)
        last_output = output[0:batch_size]
        out = self.batch_norm2(last_output)

        out_task1 = F.sigmoid(self.hid_mlp2_task1(out))
        out_task1 = self.batch_norm3(out_task1)
        out_task1 = F.sigmoid(self.hid_mlp3_task1(out_task1))
        out_task1 = self.out_mlp2_task1(out_task1)
        out_task1 = F.sigmoid(out_task1)

        out_task2 = F.relu(self.hid_mlp2_task2(out))
        out_task2 = self.batch_norm3(out_task2)
        out_task2 = F.relu(self.hid_mlp3_task2(out_task2))
        out_task2 = self.out_mlp2_task2(out_task2)
        out_task2 = F.sigmoid(out_task2)
        #         print 'out: ', out.size()
        # batch_size * task_num
        return out_task1

class MyRepresentation(nn.Module):
    def __init__(self, input_dim, hidden_dim, hid_dim, middle_result_dim, task_num):
        super(MyRepresentation, self).__init__()
        self.hidden_dim = hidden_dim
        self.lstm1 = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.batch_norm1 = nn.BatchNorm1d(hid_dim)
        # The linear layer that maps from hidden state space to tag space

        self.sample_mlp = nn.Linear(1000, hid_dim)
        self.condition_mlp = nn.Linear(hidden_dim, hid_dim)
        #         self.out_mlp1 = nn.Linear(hidden_dim, middle_result_dim)
        #         self.hid_mlp1 = nn.Linear(15+108+2*hid_dim, hid_dim)
        #         self.out_mlp1 = nn.Linear(hid_dim, middle_result_dim)

        self.lstm2 = nn.LSTM(15 + 7 + 2 + hid_dim, hidden_dim, batch_first=True)
        #         self.lstm2_binary = nn.LSTM(15+108+2*hid_dim, hidden_dim, batch_first=True)
        #         self.lstm2_binary = nn.LSTM(15+108+2*hid_dim, hidden_dim, batch_first=True)
        self.batch_norm2 = nn.BatchNorm1d(hidden_dim)
        # The linear layer that maps from hidden state space to tag space
        self.hid_mlp2_task1 = nn.Linear(hidden_dim, hid_dim)
        self.hid_mlp2_task2 = nn.Linear(hidden_dim, hid_dim)
        self.batch_norm3 = nn.BatchNorm1d(hid_dim)
        self.hid_mlp3_task1 = nn.Linear(hid_dim, hid_dim)
        self.hid_mlp3_task2 = nn.Linear(hid_dim, hid_dim)
        self.out_mlp2_task1 = nn.Linear(hid_dim, 1)
        self.out_mlp2_task2 = nn.Linear(hid_dim, 1)
        self.composer = BinaryTreeComposer(15 + 7 + 2 + hid_dim, hidden_dim)

    #         self.hidden2values2 = nn.Linear(hidden_dim, action_num)

    def init_hidden(self, hidden_dim, batch_size=1):
        # Before we've done anything, we dont have any hidden state.
        # Refer to the Pytorch documentation to see exactly
        # why they have this dimensionality.
        # The axes semantics are (num_layers, minibatch_size, hidden_dim)
        return (torch.zeros(1, batch_size, hidden_dim).cuda(),
                torch.zeros(1, batch_size, hidden_dim).cuda())

    def forward(self, operators, extra_infos, cardinalities, condition1s, condition2s, mapping):
        # condition1
        batch_size = 0
        for i in range(operators.size()[1]):
            if operators[0][i].sum(0) != 0:
                batch_size += 1
            else:
                break
        print('batch_size: ', batch_size)

        #         print (operators.size())
        #         print (extra_infos.size())
        #         print (condition1s.size())
        #         print (condition2s.size())
        #         print (samples.size())
        #         print (condition_masks.size())
        #         print (mapping.size())

        #         torch.Size([14, 133, 15])
        #         torch.Size([14, 133, 108])
        #         torch.Size([14, 133, 13, 1119])
        #         torch.Size([14, 133, 13, 1119])
        #         torch.Size([14, 133, 1000])
        #         torch.Size([14, 133, 1])
        #         torch.Size([14, 133, 2])

        num_level = condition1s.size()[0]
        num_node_per_level = condition1s.size()[1]
        num_condition_per_node = condition1s.size()[2]
        condition_op_length = condition1s.size()[3]

        inputs = condition1s.view(num_level * num_node_per_level, num_condition_per_node, condition_op_length)
        hidden = self.init_hidden(self.hidden_dim, num_level * num_node_per_level)

        out, hid = self.lstm1(inputs, hidden)
        last_output1 = hid[0].view(num_level * num_node_per_level, -1)

        # condition2
        num_level = condition2s.size()[0]
        num_node_per_level = condition2s.size()[1]
        num_condition_per_node = condition2s.size()[2]
        condition_op_length = condition2s.size()[3]

        inputs = condition2s.view(num_level * num_node_per_level, num_condition_per_node, condition_op_length)
        hidden = self.init_hidden(self.hidden_dim, num_level * num_node_per_level)

        out, hid = self.lstm1(inputs, hidden)
        last_output2 = hid[0].view(num_level * num_node_per_level, -1)

        last_output1 = F.relu(self.condition_mlp(last_output1))
        last_output2 = F.relu(self.condition_mlp(last_output2))
        last_output = (last_output1 + last_output2) / 2
        last_output = self.batch_norm1(last_output).view(num_level, num_node_per_level, -1)

        #         print (last_output.size())
        #         torch.Size([14, 133, 256])


        out = torch.cat((operators, extra_infos, cardinalities, last_output), 2)
        #         print (out.size())
        #         torch.Size([14, 133, 635])
        #         out = out * node_masks
        start = time.time()
        hidden = self.init_hidden(self.hidden_dim, num_node_per_level)
        last_level = out[num_level - 1].view(num_node_per_level, 1, -1)
        #         torch.Size([133, 1, 635])
        _, (hid, cid) = self.lstm2(last_level, hidden)
        mapping = mapping.long()
        for idx in reversed(range(0, num_level - 1)):
            mapp_left = mapping[idx][:, 0]
            mapp_right = mapping[idx][:, 1]
            pad = torch.zeros_like(hid)[:, 0].unsqueeze(1)
            next_hid = torch.cat((pad, hid), 1)
            pad = torch.zeros_like(cid)[:, 0].unsqueeze(1)
            next_cid = torch.cat((pad, cid), 1)
            hid_left = torch.index_select(next_hid, 1, mapp_left)
            cid_left = torch.index_select(next_cid, 1, mapp_left)
            hid_right = torch.index_select(next_hid, 1, mapp_right)
            cid_right = torch.index_select(next_cid, 1, mapp_right)
            # hid = (hid_left + hid_right) / 2
            # cid = (cid_left + cid_right) / 2
            last_level = out[idx].view(num_node_per_level, 1, -1)
            hid, cid = self.composer.forward(last_level, cid_left, hid_left, cid_right, hid_right)
        output = hid[0]
        #         print (output.size())
        #         torch.Size([133, 128])
        end = time.time()
        print('Forest Evaluate Running Time: ', end - start)
        last_output = output[0:batch_size]
        out = self.batch_norm2(last_output)

        out_task1 = F.relu(self.hid_mlp2_task1(out))
        out_task1 = self.batch_norm3(out_task1)
        out_task1 = F.relu(self.hid_mlp3_task1(out_task1))
        out_task1 = self.out_mlp2_task1(out_task1)
        out_task1 = F.sigmoid(out_task1)

        return out_task1