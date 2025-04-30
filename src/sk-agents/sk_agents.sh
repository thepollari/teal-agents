#!/bin/bash

APP_DIR=$(pwd)
AGENT_DIR=${APP_DIR}/agents
echo "Loading .env file from ${APP_DIR}/.env"
if [[ -f ".env" ]]; then
  source ${APP_DIR}/.env
fi

if [ "${TA_GITHUB}" == "true" ]; then
  WORK_DIR=$(mktemp -d)
  echo "Creating temp dir ${WORK_DIR}"
  cd ${WORK_DIR} || exit
  echo "Cloning ${TA_GH_ORG}/${TA_GH_REPO}#${TA_GH_BRANCH} to ${WORK_DIR}"
  git clone https://oauth2:${TA_GH_TOKEN}@github.com/${TA_GH_ORG}/${TA_GH_REPO}.git
  cd ${TA_GH_REPO} || exit
  echo "Checking out ${TA_GH_BRANCH} to ${WORK_DIR}"
  git checkout ${TA_GH_BRANCH} -- ${TA_AGENT_NAME}

  echo "Copying contents of ${TA_AGENT_NAME} to ${AGENT_DIR}"
  cd ${TA_AGENT_NAME} || exit
  cp -r . ${AGENT_DIR}
  cd ${AGENT_DIR} || exit
  echo "Removing temp dir ${WORK_DIR}"
  rm -rf ${WORK_DIR}
fi

export PATH=${PATH}:~/.local/bin
echo "Checking if additional requirements should be installed"
if [[ -f "${AGENT_DIR}/requirements.txt" ]]; then
  echo "Installing requirements from ${AGENT_DIR}/requirements.txt"
  uv pip install -r ${AGENT_DIR}/requirements.txt
fi
if [[ -f "${TA_ADDL_REQUIREMENTS}" ]]; then
  echo "Installing additional requirements from ${TA_ADDL_REQUIREMENTS}"
  uv pip install -r ${TA_ADDL_REQUIREMENTS}
fi

echo "Running SK Agent ${TA_AGENT_NAME}"
cd ${APP_DIR} || exit
uv run -- fastapi run src/sk_agents/app.py --port 8000
