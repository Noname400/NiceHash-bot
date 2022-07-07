
import nicehash

host = 'https://api-test.nicehash.com'
organisation_id = '7e5deba0-46ed-4ed0-b0c4-1d606c472e3d'
key = 'b334318e-6446-46db-a277-af2c1b42cd5b'
secret = '2b6fe4ef-5f92-4b11-958b-c3a7a6fd57e0e4bfb401-9d89-44cc-bd16-58f1a250c1cb'

private_api = nicehash.private_api(host, organisation_id, key, secret, True)
public_api = nicehash.public_api(host, True)
algorithms = public_api.get_algorithms()

new_order = private_api.create_hashpower_order('EU', 'STANDARD', 'SCRYPT', 0.123, 0, 0.005, 'aae0620c-973b-4a45-bd9c-58fb95930a8d', algorithms)
print(new_order)