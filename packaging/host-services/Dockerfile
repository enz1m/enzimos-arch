FROM docker.io/library/archlinux@sha256:97119fd9e21219b02b3c14ba256c9d3c0d031d07fc26c836c41ed793beeb5b74
ARG SERVICE
ENV HOST_SERVICE=${SERVICE}
COPY packaging/host-services /recipes
RUN /recipes/build install-deps "$HOST_SERVICE" && useradd --create-home --uid 20000 builder
USER builder
WORKDIR /home/builder
RUN /recipes/build prepare "$HOST_SERVICE"
ENTRYPOINT ["/recipes/build","package"]
