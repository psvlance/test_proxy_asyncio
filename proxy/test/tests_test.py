import unittest


class TestJWT(unittest.TestCase):
    def test_jwt(self):
        import jwt
        from proxy.project.run import get_bjwt, JWT_SECRET, JWT_ALG
        bjwt = get_bjwt()

        payload = jwt.decode(bjwt, JWT_SECRET, JWT_ALG)
        self.assertEqual(payload['user'], 'username')
