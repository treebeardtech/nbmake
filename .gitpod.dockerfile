FROM gitpod/workspace-full:latest

USER root

# Install custom tools, runtime, etc.

RUN ["apt-get", "update"]

RUN ["apt-get", "install", "-y", "zsh"]
RUN chsh -s $(which zsh)

USER gitpod

  # set the zsh theme 

ENV ZSH_THEME cloud

# RUN pip install poetry && poetry install && pytest

# Install Oh-My-Zsh

RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.2/zsh-in-docker.sh)" -- \
    -t robbyrussell \
    -p zsh-autosuggestions \
    -p zsh-syntax-highlighting

RUN git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
RUN git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

RUN sh -c "FORCE=1 $(curl -fsSL https://starship.rs/install.sh)"
RUN zsh -c 'eval "$(starship init zsh)"'

# start zsH
CMD [ "zsh" ]
