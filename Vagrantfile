Vagrant.configure("2") do |config|
    config.vm.define "default" do |default|
        default.vm.box = "generic/ubuntu2204"
        default.vm.synced_folder "./", "/vagrant"
        default.vm.provision "shell", path: "provision.sh"
    end
end