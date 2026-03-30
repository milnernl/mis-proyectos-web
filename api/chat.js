export default async function handler(req, res) {
  // Configurar CORS para todas las respuestas
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Responder a preflight (OPTIONS)
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Solo POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Método no permitido' });
  }

  const { message } = req.body;
  if (!message) {
    return res.status(400).json({ error: 'Falta el mensaje' });
  }

  const HF_TOKEN = process.env.HF_TOKEN;
  if (!HF_TOKEN) {
    return res.status(500).json({ error: 'Token de Hugging Face no configurado' });
  }

  const model = 'google/flan-t5-small';

  try {
    const response = await fetch(
      `https://api-inference.huggingface.co/models/${model}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${HF_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          inputs: `Pregunta: ${message}\nRespuesta:`,
          parameters: { max_new_tokens: 100, temperature: 0.7 }
        }),
      }
    );

    const data = await response.json();

    if (data.error) {
      console.error('Error HF:', data.error);
      return res.status(500).json({ error: data.error });
    }

    let reply = data[0]?.generated_text || "Lo siento, no pude generar una respuesta.";
    reply = reply.replace(/^Respuesta:\s*/i, '').trim();
    
    return res.status(200).json({ reply });
  } catch (error) {
    console.error(error);
    return res.status(500).json({ error: 'Error interno' });
  }
}
