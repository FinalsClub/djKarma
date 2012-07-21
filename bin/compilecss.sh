#!/bin/bash
# compiles less files to css
# TODO rm current copies of these files first
lessc ./static/less/bootstrap/bootstrap.less ./static/css/bootstrap.css
lessc ./static/less/styles.less ./static/css/styles.css
