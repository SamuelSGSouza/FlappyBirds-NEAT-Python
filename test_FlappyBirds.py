import unittest
from FlappyBirds import Bird
import pygame
"""
Passaro:
    Recebe lista de imagens
    Define rotação máxima int = 25
    Define velocidade de rotação = 20
    Define Tempo de animação int = 5

"""
class TestBird(unittest.TestCase):
    def setUp(self):
        self.bird = Bird(10, 12)
    
    def test_if_imgs_is_a_list(self):
        self.assertIsInstance(self.bird.IMGS, list)
        
    def test_if_each_img_element_is_a_pygameSurface(self):
        for input in self.bird.IMGS:
            with self.subTest(input=input):
                self.assertIsInstance(
                    input,
                    pygame.Surface,
                    msg=f"Input {input} is not a pygame.Surface instance"
                )

    def test_if_max_rotation_is_number(self):
        self.assertIsInstance(self.bird.MAX_ROTATION, (int, float))

    def test_if_max_speed_is_number(self):
        self.assertIsInstance(self.bird.ROTATION_SPEED, (int, float))

    def test_if_animation_time_is_number(self):
        self.assertIsInstance(self.bird.ANIMATION_TIME, (int, float))

    def test_var_x_isnot_num_raises_assertError(self):
        with self.assertRaises(AssertionError):
            self.bird = Bird("x", 12)

    def test_var_y_isnot_num_raises_assertError(self):
        with self.assertRaises(AssertionError):
            self.bird = Bird(12, '12')

    def test_vars_init_has_correct_type(self):
        inputs = [self.bird.ang, self.bird.speed, self.bird.height, self.bird.time, self.bird.img_count]
        for input in inputs:
            with self.subTest(input=input):
                self.assertIsInstance(
                    input,
                    (int, float),
                    msg=f"input {input} is not an Int or Float instance "
                )

    def test_selfImage_is_a_pygameSurface_instance(self):
        self.assertIsInstance(self.bird.imagem, pygame.Surface)

if __name__ == "__main__":
    unittest.main(verbosity=2)