import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import { Container, Row, Col, Card, Spinner } from 'react-bootstrap';
import './Dashboard.css';  // Archivo CSS mejorado

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#aa66cc'];

const Dashboard = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/metrics-data')
      .then(response => setData(response.data))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  if (!data) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Cargando datos...</p>
      </Container>
    );
  }

  const comprasPorUsuario = Object.entries(data.purchase.user_counts).map(([user, count], index) => ({
    name: `Usuario ${index + 1}`,
    compras: count
  }));

  const loginsPorDispositivo = Object.entries(data.login.devices).map(([device, count]) => ({
    name: device,
    value: count
  }));

  const loginsPorPlataforma = Object.entries(data.login.platforms).map(([platform, count]) => ({
    name: platform,
    value: count
  }));

  const ratingsDistribucion = data.reviews.ratings.reduce((acc, val) => {
    acc[val] = (acc[val] || 0) + 1;
    return acc;
  }, {});

  const ratingsData = Object.entries(ratingsDistribucion).map(([rating, count]) => ({
    rating,
    count
  }));

  const comprasEnTiempo = data.purchase.timestamps.map((ts, i) => ({
    timestamp: ts,
    tiempo: data.purchase.elapsed_times[i]
  })).filter(d => d.timestamp);

  return (
    <Container className="my-5">
      <h2 className="text-center mb-5 dashboard-title">📊 Dashboard de Métricas</h2>

      <Row className="mb-4">
        <Col md={6}>
          <Card className="dashboard-card shadow p-4">
            <Card.Title className="card-title">🛒 Compras por Usuario</Card.Title>
            <BarChart width={600} height={300} data={comprasPorUsuario}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="compras" fill="#4C8BF5" />
            </BarChart>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="dashboard-card shadow p-4">
            <Card.Title className="card-title">📈 Evolución de Tiempos de Compra</Card.Title>
            <LineChart width={700} height={300} data={comprasEnTiempo}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" tickFormatter={(tick) => tick.split("T")[0]} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="tiempo" stroke="#FF6600" />
            </LineChart>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={6}>
          <Card className="dashboard-card shadow p-4">
            <Card.Title className="card-title">💻 Logins por Plataforma</Card.Title>
            <PieChart width={300} height={300}>
              <Pie data={loginsPorPlataforma} dataKey="value" nameKey="name" outerRadius={100} fill="#4C8BF5" label>
                {loginsPorPlataforma.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="dashboard-card shadow p-4">
            <Card.Title className="card-title">📱 Logins por Dispositivo</Card.Title>
            <PieChart width={300} height={300}>
              <Pie data={loginsPorDispositivo} dataKey="value" nameKey="name" outerRadius={100} fill="#FF8042" label>
                {loginsPorDispositivo.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={12}>
          <Card className="dashboard-card shadow p-4">
            <Card.Title className="card-title">⭐ Distribución de Calificaciones</Card.Title>
            <BarChart width={600} height={300} data={ratingsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="rating" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#FFC300" />
            </BarChart>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;
