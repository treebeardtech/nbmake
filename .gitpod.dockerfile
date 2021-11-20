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

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

RUN sh -c "FORCE=1 $(curl -fsSL https://starship.rs/install.sh)"
RUN zsh -c 'eval "$(starship init zsh)"'


RUN curl -fsSL https://raw.githubusercontent.com/alex-treebeard/devtools/0f3f01615a9d7d73d398a739580845864108efe9/.zshrc > ~/.zshrc

# start zsH
CMD [ "zsh" ]