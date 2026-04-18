# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.11"; # or "unstable"
  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.nodejs_22
    pkgs.python3
  ];
  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
      "google.gemini-cli-vscode-ide-companion"
    ];
    # Enable previews and customize configuration
    previews = {
      enable = true;
      previews = {
        web = {
          command = [
            "bash"
            "-lc"
            "source .venv/bin/activate && HOST=0.0.0.0 PORT=$PORT python3 server.py"
          ];
          manager = "web";
        };
      };
    };
    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        setup-python = ''
          python3 -m venv .venv
          source .venv/bin/activate
          pip install -r requirements.txt
        '';
        # Open editors for the following files by default, if they exist:
        default.openFiles = [ "style.css" "main.js" "index.html" ];
      };
      # Runs when the workspace is (re)started
      onStart = {
        ensure-venv = ''
          if [ ! -d .venv ]; then
            python3 -m venv .venv
            source .venv/bin/activate
            pip install -r requirements.txt
          fi
        '';
      };
    };
  };
}
