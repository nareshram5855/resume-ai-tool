import axios from "axios";

const API = axios.create({ baseURL: "http://localhost:8002" });

export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await API.post("/api/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const deleteResume = async (fileId) => {
  const { data } = await API.delete(`/api/files/${fileId}`);
  return data;
};

export const analyzeResume = async (fileId, jdText, jdUrl) => {
  const payload = { file_id: fileId };
  if (jdUrl) payload.jd_url = jdUrl;
  else payload.jd_text = jdText;
  const { data } = await API.post("/api/analyze", payload);
  return data;
};

export const getDownloadUrl = (fileId) =>
  `http://localhost:8002/api/download/${fileId}`;
