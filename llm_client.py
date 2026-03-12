import groq

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


def _exc_summary(exc: Exception) -> str:
    parts = [f"{type(exc).__name__}: {exc}"]
    cause = getattr(exc, "__cause__", None)
    if cause:
        parts.append(f"Cause: {type(cause).__name__}: {cause}")
    context = getattr(exc, "__context__", None)
    if context and context is not cause:
        parts.append(f"Context: {type(context).__name__}: {context}")
    return " | ".join(parts)

def _json_required(prompt: str, system_prompt: str) -> bool:
    marker = "You MUST output ONLY a valid JSON object"
    return marker in (system_prompt or "") or marker in (prompt or "")


class GroqClient:
    def __init__(self, api_key, model_name="llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = groq.Groq(api_key=api_key) if api_key else None

    def generate(self, prompt, system_prompt):
        if not self.client:
            raise ValueError("Groq API key not provided.")
        try:
            json_required = _json_required(prompt, system_prompt)
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                model=self.model_name,
                temperature=0.2,
                response_format={"type": "json_object"} if json_required else None,
            )
            return response.choices[0].message.content
        except Exception as e:
            msg = _exc_summary(e)
            print(f"Groq API Error: {msg}")
            if "Connection error" in str(e) or "connection" in str(e).lower():
                raise ValueError(
                    "Groq connection error. Check internet/DNS/firewall, or set "
                    "HTTP_PROXY/HTTPS_PROXY if you're behind a corporate proxy. "
                    f"Details: {msg}"
                ) from e
            raise


class OpenAIClient:
    def __init__(self, api_key, model_name="gpt-5.2"):
        self.api_key = api_key
        self.model_name = model_name
        if not api_key:
            self.client = None
        else:
            if OpenAI is None:
                raise ImportError(
                    "OpenAI SDK not installed. Install `openai` (pip install -r requirements.txt)."
                )
            self.client = OpenAI(api_key=api_key)

    def generate(self, prompt, system_prompt):
        if not self.client:
            raise ValueError("OpenAI API key not provided.")
        try:
            kwargs = {}
            if _json_required(prompt, system_prompt):
                kwargs["text"] = {"format": {"type": "json_object"}}

            response = self.client.responses.create(
                model=self.model_name,
                instructions=system_prompt,
                input=prompt,
                temperature=0.2,
                **kwargs,
            )

            text = getattr(response, "output_text", None)
            if text is not None:
                return text

            # Fallback parsing (SDK differences).
            out = getattr(response, "output", None) or []
            for item in out:
                for content in getattr(item, "content", None) or []:
                    if getattr(content, "type", None) in ("output_text", "text"):
                        return getattr(content, "text", "")
            return ""
        except Exception as e:
            msg = _exc_summary(e)
            print(f"OpenAI API Error: {msg}")
            raise


class AutoClient:
    def __init__(
        self,
        groq_key,
        openai_key,
        groq_model="llama-3.3-70b-versatile",
        openai_model="gpt-5.2",
    ):
        self.groq_key = groq_key
        self.openai_key = openai_key
        self.groq_model = groq_model
        self.openai_model = openai_model

    def generate(self, prompt, system_prompt):
        if not self.groq_key and not self.openai_key:
            raise ValueError(
                "No API keys configured. Add a Groq and/or OpenAI key in Settings."
            )

        last_error = ""

        if self.groq_key:
            try:
                return GroqClient(self.groq_key, model_name=self.groq_model).generate(
                    prompt, system_prompt
                )
            except Exception as e:
                last_error += f"Groq Error: {e}\n"

        if self.openai_key:
            try:
                return OpenAIClient(self.openai_key, model_name=self.openai_model).generate(
                    prompt, system_prompt
                )
            except Exception as e:
                last_error += f"OpenAI Error: {e}\n"

        raise ValueError(f"Generation failed. Errors:\n{last_error}")
