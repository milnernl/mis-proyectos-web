export default async function handler(req, res) {
  // Configurar CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

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

  // Usar la nueva URL del router de Hugging Face
  const model = 'google/flan-t5-small';
  const url = `https://router.huggingface.co/hf-inference/models/${model}`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${HF_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        inputs: `Pregunta: ${message}\nRespuesta:`,
        parameters: { max_new_tokens: 100, temperature: 0.7 }
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error HF:', response.status, errorText);
      return res.status(response.status).json({ error: `Error de Hugging Face: ${response.status}` });
    }

    const data = await response.json();
    let reply = data[0]?.generated_text || "Lo siento, no pude generar una respuesta.";
    reply = reply.replace(/^Respuesta:\s*/i, '').trim();

    return res.status(200).json({ reply });
  } catch (error) {
    console.error('Error en el proxy:', error);
    return res.status(500).json({ error: 'Error interno del servidor' });
  }
}
