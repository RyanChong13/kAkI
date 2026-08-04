import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Landing from "./pages/Landing";
import Redesign from "./pages/Redesign";
import Register from "./pages/Register";
import Login from "./pages/Login";
import CoursesBrowse from "./pages/courses/Browse";
import CourseDetail from "./pages/courses/CourseDetail";

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/redesign" element={<Redesign />} />
        <Route path="/courses" element={<CoursesBrowse />} />
        <Route path="/courses/:id" element={<CourseDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </>
  );
}
