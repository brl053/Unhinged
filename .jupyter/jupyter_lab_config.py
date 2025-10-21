
# Jupyter Lab configuration for Unhinged ML/AI development
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.notebook_dir = str(Path.cwd())

# Enable extensions
c.ServerApp.jpserver_extensions = {
    'jupyter_lsp': True,
    'jupyterlab': True
}
