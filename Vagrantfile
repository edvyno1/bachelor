Vagrant.configure("2") do |config|
    config.vm.define "default" do |default|
        default.vm.box = "generic/ubuntu2204"
        default.vm.synced_folder "./", "/vagrant"
        default.vm.provision "shell", path: "provision.sh"
        default.vm.network "public_network", bridge: 'wlp0s20f3', ip: "192.168.1.201"
    end
    config.vm.define "guibuntu" do |g|
        g.vm.box = "generic/ubuntu2204"
        g.vm.synced_folder "./", "/vagrant"

        g.vm.provision "shell", path: "guiprovision.sh"
        g.vm.provider :virtualbox do |v|
            v.gui = true
            v.memory = 2048
        end
        g.vm.network "public_network", bridge: 'wlp0s20f3', ip: "192.168.1.201"
    end
end