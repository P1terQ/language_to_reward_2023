# Copyright 2023 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""A conversational chat utility for controlling MJPC."""

from typing import Any, List

from absl import app
from absl import flags
import colorama
import openai
import termcolor

from language_to_reward_2023 import confirmation_safe_executor
from language_to_reward_2023 import conversation
from language_to_reward_2023 import task_configs


_API_KEY_FLAG = flags.DEFINE_string("api_key", "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", "OpenAI API Key")
_TASK_FLAG = flags.DEFINE_enum("task", "barkour", list(task_configs.ALL_TASKS), "task to be used")
_PROMPT_FLAG = flags.DEFINE_string("prompt", "thinker_coder", "prompt to be used")
MODEL = "gpt-4"

colorama.init() # 终端彩色文本


def main(argv: List[str]) -> None:
  if len(argv) > 1:
    raise app.UsageError("Too many command-line arguments.")  # 只有一个api key

  safe_executor = confirmation_safe_executor.ConfirmationSafeExecutor() # ConfirmationSafeExecutor

  assert _TASK_FLAG.value in task_configs.ALL_TASKS # task: barkour

  openai.api_key = _API_KEY_FLAG.value
  
  task_config = task_configs.ALL_TASKS[_TASK_FLAG.value]  # task configuration: barkour config
  if _PROMPT_FLAG.value not in task_config.prompts:
    raise ValueError(
        "Invalid value for --prompt. Valid values:"
        f" {', '.join(task_config.prompts)}"
    )
    
  prompt = task_config.prompts[_PROMPT_FLAG.value]  #! prompt: PromptThinkerCoder
  # prompts={
  #     'thinker_coder': bk_prompt_thinker_coder.PromptThinkerCoder,
  #     'coder_only': bk_prompt_coder_only.PromptCoder,
  #     'low_level': bk_prompt_low_level.PromptLowLevel,
  # },
  print("Starting MJPC UI")
  
  client_class: Any = task_config.client  #! task: BarkourClient
  client = client_class(ui=True)

  try:
    # send the grpc channel to the prompt model to create stub
    prompt_model = prompt(client, executor=safe_executor) #! create prompt
    conv = conversation.Conversation(prompt_model, MODEL)
    client.reset()

    while True:
      user_command = input(termcolor.colored("User: ", "red", attrs=["bold"]))
      try:
        response = conv.send_command(user_command)  # 处理user_command，输入user_command给llm，返回response
      except Exception as e:  # pylint: disable=broad-exception-caught
        print("Planning failed, try something else... " + str(e) + "\n")
        continue

      # Final response should be code
      try:
        prompt_model.code_executor(response)  #! PromptThinkerCoder
                
      except Exception as e:  # pylint: disable=broad-exception-caught
        print("Execution failed, try something else... " + str(e) + "\n")
  finally:
    client.close()


if __name__ == "__main__":
  app.run(main)
