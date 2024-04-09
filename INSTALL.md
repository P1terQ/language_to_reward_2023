cd mujoco-mpc
mkdir build
cd build
conda activate lang2reward

1. clang
sudo apt-get install clang-12
CXX=clang++-12 CC=clang-12 cmake .. 
CC=clang-12 CXX=clang++-12 make -j 16
test: ./bin/mjpc

2. gcc(this works for the next python step)
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j 16

# install mujoco-mpc
cd ../python
python setup.py install
python "mujoco_mpc/agent_test.py"


# install l2r
cd language_to_reward_2023
pip install .


python -m language_to_reward_2023.user_interaction --api_key=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
报错无法打开/temp/__pychache__/中的文件，参照"https://github.com/google-deepmind/language_to_reward_2023/pull/2"修改
