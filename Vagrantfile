Vagrant.configure("2") do |config|
    config.vm.define "default" do |default|
        default.vm.box = "generic/ubuntu2204"
        default.vm.synced_folder "./", "/vagrant"
        default.vm.provision "shell", path: "provision.sh"
        config.vm.network "public_network", bridge: 'wlp0s20f3', ip: "192.168.1.201"
        # default.vm.provider :virtualbox do |vb|
        #     vb.customize ['modifyvm', :id, '--usb', 'on']
        #     vb.customize ['usbfilter', 'add', '0', '--target', :id, '--name', 'edimax7718un', '--vendorid', '0x7392']
        # end
    end
end