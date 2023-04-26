

# cd scripts

if [ -z "${OPENAI_API_KEY}" ]; then 
  echo "No OpenAI api key, initializing WhyBot"
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_why_bot.py" | sed "s/WhyBot/${project_dir}/g" > ../main.py
else 
  echo "Has OpenAI api key, initializing ChatGPTBot"
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_chatgpt.py" | sed "s/ChatGPTBot/${project_dir}/g" > ../main.py
fi

