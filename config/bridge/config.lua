bind_address = "*"
bind_base_port = 5555

curve_public_key = os.getenv("bridge_curve_publickey")
curve_secret_key = os.getenv("bridge_curve_secretkey")

bridgeapp_curve_publickey = os.getenv("bridge_bridgeapp_curve_publickey")
if bridgeapp_public_key then
   known_nodes = {
      { public_key = bridgeapp_curve_publickey, user_id = "bridgeapp" },
   }
end

data_dir = os.getenv("bridge_data_dir")
