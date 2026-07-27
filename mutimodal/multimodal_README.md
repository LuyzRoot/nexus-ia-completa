# Multimodal (NEXUS)

Esta pasta contém utilitários multimodais para o NEXUS:
- Image utilities (Pillow)
- OCR (pytesseract)
- Captioning (transformers / BLIP)
- Image generation (diffusers / OpenAI Images fallback)
- Audio: ASR (whisper/OpenAI) and TTS (ElevenLabs/pyttsx3)
- Pipelines that combine captioning + LLM

Instalação
- Instale requisitos conforme suas necessidades. Muitos pacotes são opcionais.
  pip install -r multimodal/requirements.txt

Uso rápido
- Capturar legenda de uma imagem:
    from multimodal import caption_image, load_image_from_path
    img = load_image_from_path("photo.jpg")
    caption = caption_image(img)

- Gerar imagem por prompt (async):
    from multimodal.image_generation import generate_image
    img_bytes = await generate_image("a red panda in a spacesuit", width=512, height=512)

- Descrever imagem + responder pergunta (async):
    from multimodal.pipelines import describe_image_and_answer
    result = await describe_image_and_answer(open("img.jpg","rb").read(), "What color is the hat?")
    print(result["caption"], result["answer"].text)

Notas
- Algumas funcionalidades (pytesseract, diffusers, whisper) dependem de binários/GPUs/configs adicionais.
- Em produção, recomenda-se isolar geração de imagens e execução de modelos pesados em serviços próprios (GPU nodes / containers).