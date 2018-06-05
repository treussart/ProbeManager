#!/usr/bin/env bash

git submodule foreach git checkout master
git checkout master

git submodule foreach git pull origin master
git pull origin master

git submodule foreach git merge develop
git merge develop

git submodule foreach git checkout develop
git checkout develop

git submodule foreach git pull origin develop
git pull origin develop
