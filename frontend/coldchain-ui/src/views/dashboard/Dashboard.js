import React, { useEffect, useState } from 'react'
import {
  CCard,
  CCardBody,
  CCardTitle,
  CRow,
  CCol,
} from '@coreui/react'
import { getLiveStatus } from '../../services/api'

const DEVICE_ID = "esp32_cc_01"
const BASE_URL = "http://10.95.52.200:8000/api"

const labelMap = {
  temp_avg: "Average Temperature",
  temp_max: "Peak Temperature",
  temp_min: "Minimum Temperature",
  temp_var: "Temperature Variation",
  humidity_avg: "Humidity",
  door_open_count: "Door Activity",
  excursion_time: "Excursion Duration",
  thermal_stress: "Thermal Stress",
  stress: "Thermal Stress"
}

const Dashboard = () => {
  const [data, setData] = useState(null)
  const [risk, setRisk] = useState('UNKNOWN')
  const [explain, setExplain] = useState({})
  const [timeLeft, setTimeLeft] = useState(null)

  const fetchData = async () => {
    try {
      // 🔹 LIVE DATA
      const liveRes = await getLiveStatus()
      if (liveRes?.data) setData(liveRes.data)

      // 🔹 RISK
      const predRes = await fetch(
        `${BASE_URL}/latest-prediction?device_id=${DEVICE_ID}`
      )
      const pred = await predRes.json()
      if (pred?.risk) setRisk(pred.risk)

      // 🔹 SHAP
      const expRes = await fetch(
        `${BASE_URL}/prediction/explain?device_id=${DEVICE_ID}`
      )
      const exp = await expRes.json()
      if (exp?.explanation) setExplain(exp.explanation)

      // 🔹 SPOIL TIME
      const spoilRes = await fetch(
        `${BASE_URL}/prediction/spoil-time?device_id=${DEVICE_ID}`
      )
      const spoil = await spoilRes.json()

      if (spoil?.time_left !== undefined) {
        // 🔥 FIX: never show 0
        setTimeLeft(Math.max(10, spoil.time_left))
      }

    } catch (e) {
      console.error('FETCH ERROR:', e)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 4000)
    return () => clearInterval(interval)
  }, [])

  if (!data) return <p>Loading...</p>

  // 🔥 SHAP FILTER
  const topFeatures = Object.entries(explain)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .filter(([_, v]) => Math.abs(v) > 0.02)
    .slice(0, 3)

  return (
    <CRow>

      {/* 🌡 Temperature */}
      <CCol sm={6} lg={3}>
        <CCard>
          <CCardBody>
            <CCardTitle>🌡 Temperature</CCardTitle>
            <h4>{data.temperature ?? '--'} °C</h4>
          </CCardBody>
        </CCard>
      </CCol>

      {/* 💧 Humidity */}
      <CCol sm={6} lg={3}>
        <CCard>
          <CCardBody>
            <CCardTitle>💧 Humidity</CCardTitle>
            <h4>{data.humidity ?? '--'} %</h4>
          </CCardBody>
        </CCard>
      </CCol>

      {/* ⚠ Risk */}
      <CCol sm={6} lg={3}>
        <CCard
          color={
            risk === 'CRITICAL'
              ? 'danger'
              : risk === 'WARNING'
              ? 'warning'
              : 'success'
          }
          textColor="white"
        >
          <CCardBody>
            <CCardTitle>⚠ Risk</CCardTitle>
            <h4>{risk}</h4>
          </CCardBody>
        </CCard>
      </CCol>

      {/* 🚪 Door */}
      <CCol sm={6} lg={3}>
        <CCard>
          <CCardBody>
            <CCardTitle>🚪 Door</CCardTitle>
            <h4>{data.door === 1 ? 'OPEN' : 'CLOSED'}</h4>
          </CCardBody>
        </CCard>
      </CCol>

      {/* ⏳ SPOIL TIME */}
      <CCol sm={6} lg={3}>
        <CCard color="dark" textColor="white">
          <CCardBody>
            <CCardTitle> Time to Spoilage</CCardTitle>

            <h4>
              {timeLeft === null
                ? "--"
                : timeLeft <= 10
                ? "⚠ <10 min"
                : `${Math.round(timeLeft)} min`}
            </h4>

            <p style={{ fontSize: '12px' }}>
              {timeLeft < 30
                ? "⚠ Immediate action!"
                : timeLeft < 60
                ? "⚠ Monitor closely"
                : " Stable"}
            </p>

          </CCardBody>
        </CCard>
      </CCol>

      {/*  SHAP + INSIGHTS */}
      <CCol sm={12}>
        <CCard className="mt-3">
          <CCardBody>

            <CCardTitle> Risk Drivers</CCardTitle>

            {topFeatures.map(([key, value]) => {
              const isRisk = value > 0

              return (
                <div key={key} style={{ marginBottom: '14px' }}>

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span><b>{labelMap[key] || key}</b></span>
                    <span style={{ color: isRisk ? '#dc3545' : '#28a745' }}>
                      {isRisk ? '🔴 Increasing Risk' : '🟢 Stabilizing'}
                    </span>
                  </div>

                  <div style={{
                    height: '8px',
                    background: '#eee',
                    borderRadius: '5px'
                  }}>
                    <div style={{
                      width: `${Math.min(Math.abs(value) * 300, 100)}%`,
                      height: '100%',
                      background: isRisk ? '#dc3545' : '#28a745'
                    }} />
                  </div>

                </div>
              )
            })}

            <hr />

            {/*  EXPLANATION */}
            <h6> Explanation</h6>

            <p>
              {risk === "CRITICAL" &&
                "Temperature conditions have exceeded safe limits, causing rapid product degradation."}

              {risk === "WARNING" &&
                "Temperature fluctuations are increasing risk and may lead to spoilage."}

              {risk === "SAFE" &&
                "Storage conditions are stable and safe."}
            </p>

            {topFeatures.length > 0 && (
              <p>
                Main cause: <b>{labelMap[topFeatures[0][0]]}</b>
              </p>
            )}

            <hr />

            {/*  ACTION */}
            <h6> Recommended Action</h6>

            {risk === "CRITICAL" && (
              <ul>
                <li>Reduce temperature immediately</li>
                <li>Close storage door</li>
                <li>Check cooling system</li>
              </ul>
            )}

            {risk === "WARNING" && (
              <ul>
                <li>Monitor temperature</li>
                <li>Reduce door usage</li>
              </ul>
            )}

            {risk === "SAFE" && (
              <p>All conditions are normal.</p>
            )}

          </CCardBody>
        </CCard>
      </CCol>

    </CRow>
  )
}

export default Dashboard