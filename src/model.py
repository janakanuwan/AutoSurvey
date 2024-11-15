import time
import requests
import json
from tqdm import tqdm
import threading
import random


class APIModel:

    def __init__(self, model, api_key, api_url) -> None:
        self.__api_key = api_key
        self.__api_url = api_url
        self.model = model

    def __req(self, text, temperature, max_try=10):
        url = f"{self.__api_url}"
        pay_load_dict = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": temperature
        }
        payload = json.dumps(pay_load_dict)
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.__api_key}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        for attempt in range(1, max_try + 1):
            try:
                response = requests.post(url, headers=headers, data=payload)
                response.raise_for_status()  # Check for HTTP errors

                response_data = response.json()  # Parse JSON directly

                # Validate and extract content
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    if isinstance(content, str):
                        return content
                    else:
                        raise TypeError(f"Unexpected content type: {type(content)}. Content: {content}")
                else:
                    raise ValueError(f"Response missing 'choices' or empty: {response_data}")

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    print(f"Rate limit exceeded (attempt {attempt}/{max_try}).")

                    # Use Retry-After if available; otherwise, linear backoff
                    retry_after = float(response.headers.get("Retry-After", attempt + random.uniform(0, max_try)))
                    print(f"Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    print(f"HTTP error: {e}. Retry attempt {attempt} of {max_try}")
                    break  # Stop retries for non-rate-limiting HTTP errors
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}. Retry attempt {attempt} of {max_try}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}. Retry attempt {attempt} of {max_try}")
            except (TypeError, ValueError) as e:
                print(f"Data error: {e}. Retry attempt {attempt} of {max_try}")
                break  # Exit retries on data-related issues

        # If all attempts fail
        print("All API request retries failed.")
        return None

    def chat(self, text, temperature=1):
        response = self.__req(text, temperature=temperature, max_try=5)
        return response

    def __chat(self, text, temperature, res_l, idx):

        response = self.__req(text, temperature=temperature)
        res_l[idx] = response
        return response

    def batch_chat(self, text_batch, temperature=0):
        max_threads = 3  # limit max concurrent threads using model API
        res_l = ['No response'] * len(text_batch)
        thread_l = []
        for i, text in zip(range(len(text_batch)), text_batch):
            thread = threading.Thread(target=self.__chat, args=(text, temperature, res_l, i))
            thread_l.append(thread)
            thread.start()
            while len(thread_l) >= max_threads:
                for t in thread_l:
                    if not t.is_alive():
                        thread_l.remove(t)
                time.sleep(0.3)  # Short delay to avoid busy-waiting

        for thread in tqdm(thread_l):
            thread.join()
        return res_l
