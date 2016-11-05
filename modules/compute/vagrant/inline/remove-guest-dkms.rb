require "vagrant"

module VagrantPlugins
  module VagrantInlinePlugin
    class Command
      def initialize(app, env)
        @app = app
	@env = env
      end

      def call(env)
	env[:ui].info("Checking if we need to remove a pre-packaged virtualbox-guest-dkms")
        env[:machine].communicate.sudo(
	  "type pacman 1> /dev/null && pacman -Q | grep virtualbox | awk '{print $1}' | xargs pacman -Rsc --noconfirm",
	  {:error_check => false}
	) do |type, data|
          output = data.to_s.strip()
          if output.include? "removing virtualbox-guest-dkms"
	    env[:ui].info("Uninstalled pre-packaged virtualbox-guest-dkms")
            reboot(env)
          end
        end
        @app.call(env)
      end

      def reboot(env)
        env[:ui].info("Rebooting to unload the dkms kernel module")
        env[:machine].action(:reload, :provision_enabled => false)
        begin
          sleep 1
        end until env[:machine].communicate.ready?
      end
    end
  end

  class Plugin < Vagrant.plugin("2")
    name "Remove virtualbox-guest-dkms before running vagrant-vbguest"

    action_hook(:VagrantInlinePlugin) do |hook|
      hook.after(
        Vagrant::Action::Builtin::WaitForCommunicator, 
	VagrantInlinePlugin::Command
      )
    end
  end
end
