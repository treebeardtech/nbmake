FROM gitpod/workspace-full:latest

USER root

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "zsh"]
RUN chsh -s $(which zsh)

USER gitpod

ENV ZSH_THEME cloud

RUN sh -c "FORCE=1 $(curl -fsSL https://starship.rs/install.sh)"


RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.2/zsh-in-docker.sh)" -- \
    -t robbyrussell \
    -p zsh-autosuggestions \
    -p zsh-syntax-highlighting

RUN git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
RUN git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

RUN echo '\neval "$(starship init zsh)"' >> ~/.zshrc
RUN echo '\nexport PIP_USER=no' >> ~/.zshrc
RUN echo '\neval "$(pyenv init -)"' >> ~/.zshrc

CMD [ "zsh" ]
