import React, { useEffect, useState } from 'react'
import {
  CCard,
  CCardBody,
  CCardHeader,
} from '@coreui/react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts'

const Storage = () => {
  const [sensorData, setSensorData] = useState([])
  const [trendData, setTrendData] = useState([])

  const fetchData = async () => {
    // 🔵 LIVE SENSOR
    const res1 = await fetch("http://localhost:8000/api/storage/history?device_id=esp32_cc_01")
    const data1 = await res1.json()

    setSensorData(data1.data.map((d, i) => ({
      index: i,
      temperature: d.temperature,
      humidity: d.humidity
    })))

    // 🔴 LSTM TREND
    const res2 = await fetch("http://localhost:8000/api/prediction/lstm-trend?device_id=esp32_cc_01")
    const data2 = await res2.json()

    setTrendData(data2.trend.map((val, i) => ({
      index: i,
      risk: val
    })))
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <>
      {/* 🔵 SENSOR CHART */}
      <CCard>
        <CCardHeader>🌡 Live Temperature & Humidity</CCardHeader>
        <CCardBody>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={sensorData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="index" />
              <YAxis />
              <Tooltip />

              <Line dataKey="temperature" stroke="#1976d2" strokeWidth={2} />
              <Line dataKey="humidity" stroke="#2e7d32" strokeWidth={2} />

            </LineChart>
          </ResponsiveContainer>
        </CCardBody>
      </CCard>

      {/* 🔴 LSTM TREND CHART */}
      <CCard style={{ marginTop: '20px' }}>
        <CCardHeader>⚠ LSTM Risk Trend (0 = Safe, 1 = Risk)</CCardHeader>
        <CCardBody>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="index" />
              <YAxis domain={[0, 1]} ticks={[0, 1]} />
              <Tooltip />

              <Line
                type="stepAfter"
                dataKey="risk"
                stroke="#d32f2f"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </CCardBody>
      </CCard>
    </>
  )
}

export default Storage