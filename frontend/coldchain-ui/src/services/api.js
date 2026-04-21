import axios from 'axios'


const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})
export const getStorageHistory = (deviceId = 'ST01') => api.get(`/storage/history?device_id=${deviceId}`)

export const getLiveStatus = () => api.get('/live-status')
export const getTransportLive = () => api.get('/transport/live')

export const ingestTransport = (payload) =>api.post('/ingest/transport', payload)

export const getTransportRoute = (params) =>api.get('/transport/route', { params })

export const getLatestPrediction = (deviceId) => api.get(`/latest-prediction?device_id=${deviceId}`)
