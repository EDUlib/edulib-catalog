ARG NGINX_IMAGE_NAME=fundocker/openshift-nginx
ARG NGINX_IMAGE_TAG=1.13
ARG STATIC_ROOT=/data/static

# to build image use : docker build -t imageName .
# ---- Nginx ----
FROM ${NGINX_IMAGE_NAME}:${NGINX_IMAGE_TAG} as nginx

ARG STATIC_ROOT

RUN mkdir -p ${STATIC_ROOT}

COPY --from=collector ${STATIC_ROOT} ${STATIC_ROOT}
COPY conf.d/ecs.conf /etc/nginx/conf.d/default.conf