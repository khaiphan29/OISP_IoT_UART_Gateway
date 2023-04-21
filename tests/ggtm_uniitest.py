import sys, unittest, cv2
sys.path.append('../IOT_LAB_MANUALS')
from uart_gateway.ai_models.AI_GGTM import GGTeachableMachineHelper


class TestGGTM(unittest.TestCase):
    img_number = 1
    detector = GGTeachableMachineHelper()
    def test_1(self):
        filename = "tests/image_test/" + str(TestGGTM.img_number) + ".jpg"
        image = cv2.imread(filename)
        TestGGTM.img_number += 1
        self.assertEqual(TestGGTM.detector.image_detector(image), "Không đeo khẩu trang\n")

    def test_2(self):
        filename = "tests/image_test/" + str(TestGGTM.img_number) + ".jpg"
        image = cv2.imread(filename)
        TestGGTM.img_number += 1
        self.assertEqual(TestGGTM.detector.image_detector(image), "Không đeo khẩu trang\n")

    def test_3(self):
        filename = "tests/image_test/" + str(TestGGTM.img_number) + ".jpg"
        image = cv2.imread(filename)
        TestGGTM.img_number += 1
        self.assertEqual(TestGGTM.detector.image_detector(image), "Không đeo khẩu trang\n")


    def test_4(self):
        filename = "tests/image_test/" + str(TestGGTM.img_number) + ".jpg"
        image = cv2.imread(filename)
        TestGGTM.img_number += 1
        self.assertEqual(TestGGTM.detector.image_detector(image), "Không đeo khẩu trang\n")


    def test_5(self):
        filename = "tests/image_test/" + str(TestGGTM.img_number) + ".jpg"
        image = cv2.imread(filename)
        TestGGTM.img_number += 1
        self.assertEqual(TestGGTM.detector.image_detector(image), "Không có người\n")

    def test_6(self):
        filename = "tests/image_test/" + str(TestGGTM.img_number) + ".jpg"
        image = cv2.imread(filename)
        TestGGTM.img_number += 1
        self.assertEqual(TestGGTM.detector.image_detector(image), "Không có người\n")

    def test_7(self):
        filename = "tests/image_test/" + str(TestGGTM.img_number) + ".jpg"
        image = cv2.imread(filename)
        TestGGTM.img_number += 1
        self.assertEqual(TestGGTM.detector.image_detector(image), "Đeo khẩu trang\n")

    def test_8(self):
        filename = "tests/image_test/" + str(TestGGTM.img_number) + ".jpg"
        image = cv2.imread(filename)
        TestGGTM.img_number += 1
        self.assertEqual(TestGGTM.detector.image_detector(image), "Đeo khẩu trang\n")


    def test_9(self):
        filename = "tests/image_test/" + str(TestGGTM.img_number) + ".jpg"
        image = cv2.imread(filename)
        TestGGTM.img_number += 1
        self.assertEqual(TestGGTM.detector.image_detector(image), "Đeo khẩu trang\n")

if __name__=='__main__':
	unittest.main()