import { trace } from "@opentelemetry/api";

const tracer = trace.getTracer("langwatch.prompts", "0.0.1");

export interface LangWatchPrompt {
  id: string;
  name: string;
  version: number;
  versionId: string;
  versionCreatedAt: string;
  model: string;
  prompt: string;
  updatedAt: string;
  messages: Message[];
  response_format: any;
}

export interface Message {
  role: string;
  content: string;
}

export async function getPrompt(id: string): Promise<LangWatchPrompt> {
  return await tracer.startActiveSpan("langwatch.get_prompt", async (span) => {
    span.setAttribute("langwatch.prompt.id", id);

    const options = {
      method: "GET",
      headers: { "X-Auth-Token": process.env.LANGWATCH_API_KEY ?? "" },
    };

    const response = await fetch(`https://app.langwatch.ai/api/prompts/${id}`, options);
    const prompt = await response.json() as LangWatchPrompt;

    span.setAttribute("langwatch.prompt.version.id", prompt.versionId);
    span.setAttribute("langwatch.prompt.version.number", prompt.version);

    span.end();
    return prompt;
  });
}
