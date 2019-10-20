import sys, os, unittest
PARENT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/../"
sys.path.append(PARENT_DIR)
TEST_IMAGE_DIR = os.path.dirname(os.path.realpath(__file__)) + "/testing_images/"

from deformation_measurement import DIC_NR
import numpy as np
from PIL import Image
from scipy.interpolate import RectBivariateSpline

class Test_DIC_NR(unittest.TestCase):
	#For quite a few of these tests I have set them up with subset size 11
	#In the case where the image is 40x40, this means Xmin,Ymin,Xp,Yp,Xmax & Ymax should all be 20
	def test_interpolation(self):
		#old testing, look to below functions for testing of actual code

		test_image_1 = np.array(Image.open(TEST_IMAGE_DIR + "ref50.bmp").convert('LA')) # numpy.array
		#print(test_image_1.shape)
		#print(test_image_1)
		test_image_b = test_image_1.astype('d')
		#print(test_image_b.shape)
		#print(test_image_b)

		X_size, Y_size, _tmp = test_image_b.shape
		#print(X_size, Y_size, _tmp)

		col1 = test_image_b[48,0,0]
		col2 = test_image_b[49,0,0]

		test_image_c = test_image_b[:,:,0]
		#print(test_image_c)

		Y_size, X_size,tmp = test_image_b.shape

		X_defcoord = np.arange(0, X_size, dtype=int) # Maybe zero?
		Y_defcoord = np.arange(0, Y_size, dtype=int)

		interp = RectBivariateSpline(X_defcoord, Y_defcoord, test_image_b[:,:,0], kx=5, ky=5)
		result1 = interp.ev(48,0)
		result2 = interp.ev(48.5,0)
		result3 = interp.ev(49,0)

		interp_res = np.empty([50,50])

		for y in range(50):
			for x in range(50):
				interp_res[x][y] = interp.ev(x,y)

		#savetxt_compact("image_actual", test_image_c)
		#savetxt_compact("deform", interp_res)
		'''
		print(result1)
		print(result2)
		print(result3)

		print(col1)
		print(col2)
		'''

	def test_initial_guess(self):

		#TEST 1
		#moving "image" all to right by 1, u = 1, v = 0
		#check the logic that u & v are indexed correctly
		ref_img = np.expand_dims(np.reshape(np.arange(40*40), (40,40)), axis = 2)
		ref_img = np.insert(ref_img, 1, 0, axis = 2)
		def_img = np.roll(ref_img.copy(), 1, axis = 1)

		dicr_1 = DIC_NR()
		dicr_1.set_parameters(TEST_IMAGE_DIR + "ref50.bmp", TEST_IMAGE_DIR + "def50.bmp", 11, [0,0])
		dicr_1.initial_guess(ref_img, def_img)

		print(dicr_1.q_k)

		self.assertEqual(dicr_1.q_k[0], 1)
		self.assertEqual(dicr_1.q_k[1], 0)

		#TEST 2
		#comparing the same image with itself, u & v should equal 0
		dicr = DIC_NR()
		dicr.set_parameters(TEST_IMAGE_DIR + "ref50.bmp", TEST_IMAGE_DIR + "ref50.bmp", 11, [0,0])
		dicr.initial_guess(ref_img, ref_img)

		self.assertEqual(dicr.q_k[0], 0)
		self.assertEqual(dicr.q_k[1], 0)

	def test_fit_spline(self):

		test_image_1 = np.array(Image.open(TEST_IMAGE_DIR + "ref50.bmp").convert('LA')) # numpy.array
		test_image_1 = test_image_1.astype('d')

		actual_val_48_0 = test_image_1[48,0,0]
		actual_val_49_0 = test_image_1[49,0,0]

		#Note: this is using same image as ref and def
		dicnr = DIC_NR()
		dicnr.set_parameters(TEST_IMAGE_DIR + "ref50.bmp", TEST_IMAGE_DIR + "ref50.bmp", 11, [0,0])
		dicnr.fit_spline()

		result1 = dicnr.def_interp.ev(48,0)
		result2 = dicnr.def_interp.ev(48.5,0)
		result3 = dicnr.def_interp.ev(49,0)

		print("Actual values at x? 48,49 y:0")
		print(actual_val_48_0)
		print(actual_val_49_0)

		print("Interpolated values at x? 48, 48.5, 49 y:0")
		print(result1)
		print(result2)
		print(result3)

	def test_whole(self):
		dic = DIC_NR()
		dic.set_parameters(TEST_IMAGE_DIR + "ref50.bmp", TEST_IMAGE_DIR + "def50.bmp", 7, [0, 0])
		print("Not running whole calculation")
		'''result = dic.calculate()
		x,y,z = result.shape
		sav = np.swapaxes(result, 2, 1).reshape((x, y*z), order='A')

		savetxt_compact("output", sav)'''
		
def savetxt_compact(fname, x, fmt="%.6g", delimiter=','):
	with open(f"compact_{fname}.csv", 'w+') as fh:
		for row in x:
			line = delimiter.join("0" if value == 0 else fmt % value for value in row)
			fh.write(line + '\n')

def savetxt_compact_matlab(fname, x, fmt="%.6g", delimiter=','):
	with open(f"matlab_{fname}.csv", 'w+') as fh:
		for row in x:
			line = delimiter.join("0" if value == 0 else fmt % value for value in row)
			fh.write(line + '\n')
