import React, { useState } from 'react'
import {
  CCard, CCardBody, CCardHeader,
  CRow, CCol, CButton, CFormInput
} from '@coreui/react'

import {
  MapContainer, TileLayer, Marker, Popup, Polyline
} from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

import {
  ingestTransport,
  getTransportRoute
} from '../../services/api'

import L from 'leaflet'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: icon,
  shadowUrl: iconShadow,
})

const Transport = () => {

  const DEVICE_ID = "esp32_cc_01"

  const [routes, setRoutes] = useState(null)
  const [mapCenter, setMapCenter] = useState([28.6139, 77.2090])

  const [transportRisk, setTransportRisk] = useState("UNKNOWN")

  const [form, setForm] = useState({
    origin_lat: '',
    origin_lon: '',
    dest_lat: '',
    dest_lon: '',
  })

  /* =============================
     INPUT HANDLER
     ============================= */
  const onChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value })

  /* =============================
     MAIN ANALYSIS
     ============================= */
  const analyzeTransport = async () => {
    try {
      const origin = [
        parseFloat(form.origin_lat),
        parseFloat(form.origin_lon),
      ]

      const dest = [
        parseFloat(form.dest_lat),
        parseFloat(form.dest_lon),
      ]

      if (origin.includes(NaN) || dest.includes(NaN)) {
        alert("Please enter valid coordinates")
        return
      }

      // Move map
      setMapCenter(origin)

      // 🔥 1. Ingest minimal data
      await ingestTransport({
        device_id: DEVICE_ID,
        latitude: origin[0],
        longitude: origin[1],
        timestamp: new Date().toISOString(),
      })

      // 🔥 2. Get route suggestions
      const res = await getTransportRoute({
        device_id: DEVICE_ID,
        origin_lat: origin[0],
        origin_lon: origin[1],
        dest_lat: dest[0],
        dest_lon: dest[1],
      })

      setRoutes(res.data)

      // 🔥 3. ML Prediction (POST)
      const pred = await fetch("http://localhost:8000/api/transport/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          device_id: DEVICE_ID,
          origin_lat: origin[0],
          origin_lon: origin[1],
          dest_lat: dest[0],
          dest_lon: dest[1]
        })
      })

      const predData = await pred.json()
      setTransportRisk(predData.risk)

    } catch (err) {
      console.error("TRANSPORT ERROR:", err)
      alert("Something went wrong. Check backend.")
    }
  }

  return (
    <>
      {/* =============================
          🚚 TRANSPORT RISK
         ============================= */}
      <CCard className="mb-4">
        <CCardHeader>🚚 Transport Risk</CCardHeader>
        <CCardBody>
          <h2
            style={{
              color:
                transportRisk === "CRITICAL"
                  ? "red"
                  : transportRisk === "WARNING"
                  ? "orange"
                  : "green",
            }}
          >
            {transportRisk}
          </h2>
        </CCardBody>
      </CCard>

      {/* =============================
          📍 INPUT
         ============================= */}
      <CCard className="mb-4">
        <CCardHeader>📍 Route Input</CCardHeader>
        <CCardBody>
          <CRow>

            <CCol lg={6}>
              <CFormInput
                name="origin_lat"
                placeholder="Origin Latitude"
                onChange={onChange}
              />
            </CCol>

            <CCol lg={6}>
              <CFormInput
                name="origin_lon"
                placeholder="Origin Longitude"
                onChange={onChange}
              />
            </CCol>

            <CCol lg={6}>
              <CFormInput
                name="dest_lat"
                placeholder="Destination Latitude"
                onChange={onChange}
              />
            </CCol>

            <CCol lg={6}>
              <CFormInput
                name="dest_lon"
                placeholder="Destination Longitude"
                onChange={onChange}
              />
            </CCol>

          </CRow>

          <CButton color="info" className="mt-3" onClick={analyzeTransport}>
            Analyze & Suggest Route
          </CButton>
        </CCardBody>
      </CCard>

      {/* =============================
          🗺 MAP
         ============================= */}
      <CCard className="mb-4">
        <CCardHeader>🗺 Route Visualization</CCardHeader>
        <CCardBody style={{ height: 450 }}>
          <MapContainer
            center={mapCenter}
            zoom={12}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

            <Marker position={mapCenter}>
              <Popup>
                📦 Device: {DEVICE_ID} <br />
                ⚠ Risk: {transportRisk}
              </Popup>
            </Marker>

            {/* Best Route */}
            {routes?.best_route?.geometry && (
              <Polyline
                positions={routes.best_route.geometry}
                pathOptions={{ color: 'blue', weight: 6 }}
              />
            )}

            {/* Alternatives */}
            {routes?.alternatives?.map((r, i) => (
              <Polyline
                key={i}
                positions={r.geometry}
                pathOptions={{ color: 'orange', dashArray: '5,10' }}
              />
            ))}

          </MapContainer>
        </CCardBody>
      </CCard>

      {/* =============================
          📊 ROUTE DETAILS
         ============================= */}
      {routes && (
        <CCard>
          <CCardHeader>🛣 Route Decision</CCardHeader>
          <CCardBody>

            <h5>✅ Recommended Route</h5>
            <p><b>ETA:</b> {routes.best_route.eta} min</p>
            <p><b>Distance:</b> {routes.best_route.distance_km} km</p>
            <p><b>Risk:</b> {(routes.best_route.risk * 100).toFixed(1)}%</p>
            <p><b>Cost:</b> {routes.best_route.cost}</p>

            <hr />

            <h5>🟡 Alternatives</h5>
            {routes.alternatives.length === 0 && <p>No alternatives</p>}

            {routes.alternatives.map((r, i) => (
              <div key={i}>
                <p><b>Option {i + 1}</b></p>
                <p>ETA: {r.eta} min</p>
                <p>Distance: {r.distance_km} km</p>
                <p>Risk: {(r.risk * 100).toFixed(1)}%</p>
                <p>Cost: {r.cost}</p>
              </div>
            ))}

          </CCardBody>
        </CCard>
      )}
    </>
  )
}

export default Transport