import { uploadPDF, sendQuery, appendMessage, clearInput } from './helper.js';

let sessionId = null;

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const loadPdfBtn = document.getElementById('load-pdf-btn');
    const sendBtn = document.getElementById('send-btn');
    const textInput = document.getElementById('text-input');

    loadPdfBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async () => {
        const file = fileInput.files[0];
        if (!file) return alert("Please select a PDF to upload.");

        const uploadingMsg = appendMessage('<strong>Bot:</strong> Uploading PDF...');
        try {
            const result = await uploadPDF(file);
            sessionId = result.session_id;
            uploadingMsg.remove();

            appendMessage(`<strong>Bot:</strong> PDF "<em>${file.name}</em>" uploaded successfully.`);
            clearInput('file-input');
        } catch (error) {
            console.error(error);
            uploadingMsg.remove();
            appendMessage('<strong>Bot:</strong> Error uploading PDF.');
        }
    });

    sendBtn.addEventListener('click', async () => {
        const question = textInput.value.trim();
        if (!question || !sessionId) return alert("Please upload a PDF and type a question.");

        appendMessage(`<strong>You:</strong> ${question}`, 'user-message');
        const thinkingMsg = appendMessage('<strong>Bot:</strong> Thinking...');

        try {
            const { answer } = await sendQuery(sessionId, question);
            thinkingMsg.remove();
            appendMessage(`<strong>Bot:</strong> ${answer || 'No answer found.'}`);
        } catch (error) {
            console.error(error);
            thinkingMsg.remove();
            appendMessage('<strong>Bot:</strong> Error retrieving answer.');
        }

        clearInput('text-input');
    });
});
