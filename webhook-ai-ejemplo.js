/**
 * Ejemplo de Integración de Webhooks con IA (Fase 3 - Escalabilidad)
 * 
 * En lugar de solo abrir WhatsApp, este script envía los datos del cliente de forma invisible
 * a una herramienta de automatización como Zapier, Make (Integromat) o n8n.
 * 
 * Flujo:
 * 1. El cliente llena el formulario en la web.
 * 2. El script envía los datos por POST (fetch) al Webhook.
 * 3. Make/Zapier recibe los datos -> Lo guarda en Google Sheets/PipeDrive CRM.
 * 4. Make/Zapier conecta con OpenAI (ChatGPT) para clasificar la urgencia del lead.
 * 5. Si es "inundación", dispara un SMS al técnico. Si es normal, agenda recordatorio.
 * 6. (Opcional) Abre WhatsApp para que el cliente hable de inmediato.
 */

function bindLeadFormAdvanced() {
    const form = document.querySelector("#leadForm");
    if (!form) return;
  
    // REEMPLAZA ESTO por la URL real de tu Webhook en Make o Zapier
    const WEBHOOK_URL = "https://hook.us1.make.com/tu-codigo-secreto-de-webhook";
  
    form.addEventListener("submit", async e => {
      e.preventDefault();
      
      const fd = new FormData(form);
      const payload = {
        nombre: (fd.get("nombre") || "").toString().trim(),
        comuna: (fd.get("comuna") || "").toString().trim(),
        problema: (fd.get("problema") || "").toString().trim(),
        urgencia: (fd.get("urgencia") || "").toString().trim(),
        utms: readUTMs(), // Adjuntamos las UTMs guardadas en localStorage
        timestamp: new Date().toISOString()
      };
  
      // 1. Enviar datos al CRM / Automatización en segundo plano
      try {
        // Ejecutamos el fetch de forma asíncrona pero sin bloquear la UX
        fetch(WEBHOOK_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });
      } catch (error) {
        console.error("Error enviando al CRM:", error);
      }
  
      // 2. Generar el mensaje tradicional de WhatsApp (Como lo tienen ahora)
      const msg = 
`Hola, soy ${payload.nombre || "—"}.
Comuna/sector: ${payload.comuna || "—"}
Motivo: ${payload.problema || "—"}
Urgencia: ${payload.urgencia || "—"}
  
Quiero agendar una video inspección y recibir informe técnico.`;
  
      // Disparamos evento de Analytics
      trackEvent("generate_lead_webhook", {
        method: "form_to_whatsapp_and_crm",
        page: location.pathname
      });
  
      // 3. Abrir WhatsApp para mantener la inmediatez
      window.open(buildWhatsAppLink(msg), "_blank", "noopener,noreferrer");
      form.reset();
    });
  }
  
