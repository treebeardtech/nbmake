FROM gitpod/workspace-full:latest

USER root

# Install custom tools, runtime, etc.

RUN ["apt-get", "update"]

RUN ["apt-get", "install", "-y", "zsh"]
RUN chsh -s $(which zsh)

USER gitpod

  # set the zsh theme 

ENV ZSH_THEME cloud

# Install Oh-My-Zsh

RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.2/zsh-in-docker.sh)" -- \
    -t robbyrussell

RUN sh -c "FORCE=1 $(curl -fsSL https://starship.rs/install.sh)"
RUN zsh -c 'eval "$(starship init zsh)"'

# start zsH
CMD [ "zsh" ]
