# -*- coding: utf-8 -*-

import torch
import torch.nn.functional as F

class ComplexMixture(torch.nn.Module):

    def __init__(self, average_weights=False):
        super(ComplexMixture, self).__init__()
        self.average_weights = average_weights

    def forward(self, inputs):

        if not isinstance(inputs, list):
            raise ValueError('This layer should be called '
                             'on a list of 2/3 inputs.')

        if len(inputs) != 3 and len(inputs) != 2:
            raise ValueError('This layer should be called '
                            'on a list of 2/3 inputs.'
                            'Got ' + str(len(inputs)) + ' inputs.')

        input_real = torch.unsqueeze(inputs[0], dim=3) #shape: (None, 60, 300, 1)
        input_imag = torch.unsqueeze(inputs[1], dim=3) #shape: (None, 60, 300, 1)
        
        input_real_transpose = torch.unsqueeze(inputs[0], dim=2) #shape: (None, 60, 1, 300)
        input_imag_transpose = torch.unsqueeze(inputs[1], dim=2) #shape: (None, 60, 1, 300)


        # output = (input_real+i*input_imag)(input_real_transpose-i*input_imag_transpose)
        output_real = torch.matmul(input_real, input_real_transpose) + torch.matmul(input_imag, input_imag_transpose) #shape: (None, 60, 300, 300)
        output_imag = torch.matmul(input_imag, input_real_transpose) - torch.matmul(input_real, input_imag_transpose) #shape: (None, 60, 300, 300)

        if self.average_weights:
            output_r = torch.mean(output_real, dim=1)
            output_i = torch.mean(output_imag, dim=1)

        else:
            if inputs[2].dim() == 2:
                weight = torch.unsqueeze(torch.unsqueeze(inputs[2], dim=-1), dim=-1)
            else:
                weight = torch.unsqueeze(inputs[2], dim=-1)
            
            output_real = output_real * weight
            output_r = torch.sum(output_real, dim=1)  #shape: (None, 300, 300)
            output_imag = output_imag * weight
            output_i = torch.sum(output_imag, dim=1)  #shape: (None, 300, 300)

        return [output_r, output_i]

def test():
    mixture = ComplexMixture()
    a = torch.randn(3, 4, 10)
    b = torch.randn(3, 4, 10)
    c = torch.randn(3, 4, 1)
    mix = mixture([a, b, c])
    print(mix)
    if mix[0].dim() == 3:
        print('ComplexMixture Test Passed.')
    else:
        print('ComplexMixture Test Failed.')

if __name__ == '__main__':
    test()