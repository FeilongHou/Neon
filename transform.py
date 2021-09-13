def transform(self, x, y):
    return self.transform_3D(x, y)
    return x, y

def transform_3D(self, x, y):
    '''
    Transform the perspective from 2D into 3D
    '''
    lin_y = (y / self.height) * self.perspective_point_y

    diff = x - self.perspective_point_x
    proportion = 1 - (lin_y / self.perspective_point_y)   # change to height for differnt effect
    proportion = pow(proportion, 2)

    tr_x = self.perspective_point_x + diff * proportion
    tr_y = self.perspective_point_y * (1 - proportion)

    return int(tr_x), int(tr_y)