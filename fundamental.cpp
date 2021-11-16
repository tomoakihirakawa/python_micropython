#define NOMINMAX
#define _CRT_SECURE_NO_WARNINGS
#include "../../include/fundamental.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <tuple>

#include "../../include/InterpolationRBF.hpp"
#include "../../include/Network.hpp"
#include "../../include/rootFinding.hpp"
/* ------------------------------------------------------ */
PYBIND11_MODULE(fundamental, m)
{
	/* ------------------------------------------------------ */
	m.doc() = "fundamental module";
	/* ------------------------------------------------------ */
	m.def("GaussianQuadratureWeights", &GaussianQuadratureWeights, "");
	m.def("SingularGaussianQuadratureWeights", &SingularGaussianQuadratureWeights, "");
	m.def("GQW", &GaussianQuadratureWeights, "");
	m.def("SGQW", &SingularGaussianQuadratureWeights, "");
	/* ------------------------------------------------------ */
	m.def("Inverse", &Inverse, "");
	/* ------------------------------------------------------ */
	m.def("Subdivide", [](double a, double b, int n)
		  { return Subdivide(a, b, n); });
	/* ------------------------------------------------------ */
	m.def("Flatten", [](const VV_d &U)
		  { return Flatten(U); });
	m.def("Flatten", [](const VV_netPp &U)
		  { return Flatten(U); });
	m.def("Flatten", [](const VV_netFp &U)
		  { return Flatten(U); });
	/* ------------------------------------------------------ */
	m.def("Join", [](const V_d &U, const V_d &V)
		  { return Join(U, V); });
	m.def("Join", [](const VV_d &U, const VV_d &V)
		  { return Join(U, V); });
	/* ------------------------------------------------------ */
	m.def("Times", [](const V_d &U, const V_d &V)
		  { return U * V; });
	m.def("Times", [](const V_d &U, const double d)
		  { return U * d; });
	m.def("Times", [](const double d, const V_d &U)
		  { return U * d; });
	/* ------------------------------------------------------ */
	m.def("__div__", [](const double d, const Tddd &U)
		  { return d / U; });
	m.def("__div__", [](const Tddd &U, const double d)
		  { return U / d; });
	m.def("__div__", [](const Tddd &V, const Tddd &U)
		  { return V / U; });
	m.def("Divide", [](const double d, const Tddd &U)
		  { return d / U; });
	m.def("Divide", [](const Tddd &U, const double d)
		  { return U / d; });
	m.def("Divide", [](const Tddd &V, const Tddd &U)
		  { return V / U; });
	//
	m.def("Divide", [](const VV_d &U, const double d)
		  { return U / d; });
	m.def("Divide", [](const V_d &U, const double d)
		  { return U / d; });
	m.def("Divide", [](const double d, const V_d &U)
		  { return d / U; });
	/* ------------------------------------------------------ */
	m.def("Dot", [](const V_d &U, const V_d &V)
		  { return Dot(U, V); });
	m.def("Dot", [](const V_d &U, const VV_d &V)
		  { return Dot(U, V); });
	m.def("Dot", [](const VV_d &U, const V_d &V)
		  { return Dot(U, V); });
	m.def("Dot", [](const VV_d &U, const VV_d &V)
		  { return Dot(U, V); });
	/* ------------------------------------------------------ */
	m.def("Cross", [](const V_d &U, const V_d &V)
		  { return Cross(U, V); });
	/* ------------------------------------------------------ */
	m.def("Max", [](const V_d &U)
		  { return Max(U); });
	/* ------------------------------------------------------ */
	m.def("Min", [](const V_d &U)
		  { return Min(U); });
	/* ------------------------------------------------------ */
	m.def("Total", [](const V_d &U)
		  { return std::accumulate(U.cbegin(), U.cend(), 0.); });
	/* ------------------------------------------------------ */
	m.def("Minus", [](const V_d &U)
		  { return -U; });
	/* ------------------------------------------------------ */
	m.def("Subtract", [](const Tddd &U, const Tddd &V)
		  { return U - V; });
	//
	m.def("Subtract", [](const V_d &U, const V_d &V)
		  { return U - V; });
	m.def("Subtract", [](const V_d &U, const VV_d &V)
		  { return U - V; });
	m.def("Subtract", [](const VV_d &U, const V_d &V)
		  { return U - V; });
	m.def("Subtract", [](const VV_d &U, const VV_d &V)
		  { return U - V; });
	m.def("Subtract", [](const V_d &U, const double a)
		  { return U - a; });
	m.def("Subtract", [](const double a, const V_d &U)
		  { return a - U; });
	/* ------------------------------------------------------ */
	m.def("Add", [](const V_d &U, const V_d &V)
		  { return U + V; });
	m.def("Add", [](const V_d &U, const VV_d &V)
		  { return U + V; });
	m.def("Add", [](const VV_d &U, const V_d &V)
		  { return U + V; });
	m.def("Add", [](const VV_d &U, const VV_d &V)
		  { return U + V; });
	m.def("Add", [](const V_d &U, const double a)
		  { return U + a; });
	m.def("Add", [](const double a, const V_d &U)
		  { return U + a; });
	/* ------------------------------------------------------ */
	m.def("Norm", [](const V_d &V)
		  { return Norm(V); });
	m.def("Normalize", [](const V_d &V)
		  { return Normalize(V); });
	/* ------------------------------------------------------ */
	m.def("Transpose", [](const VV_d &M)
		  { return Transpose(M); });
	m.def("Transpose", [](const VVV_d &M)
		  { return Transpose(M); });
	m.def("RandomReal", [](const V_d &minmax)
		  { return RandomReal(minmax); });
	/* ------------------------------------------------------ */
	/* ------------------------------------------------------ */
	pybind11::class_<geometry::Triangle>(m, "Triangle")
		.def(pybind11::init<const T3Tddd &, double>());
	pybind11::class_<geometry::Sphere>(m, "Sphere")
		.def(pybind11::init<const Tddd &, const double>());
	pybind11::class_<geometry::CoordinateBounds>(m, "CoordinateBounds")
		.def(pybind11::init<const geometry::Triangle &>())
		.def(pybind11::init<const geometry::Sphere &>())
		.def_readwrite("bounds", &geometry::CoordinateBounds::bounds);
	/* ------------------------------------------------------ */
	pybind11::class_<InterpolationVectorRBF>(m, "InterpolationVectorRBF")
		.def(pybind11::init<const VV_d &, const VV_d &>())
		.def("__call__", &InterpolationVectorRBF::operator())
		.def("div", &InterpolationVectorRBF::div)
		.def("grad", &InterpolationVectorRBF::grad)
		.def("N", pybind11::overload_cast<const V_d &>(&InterpolationVectorRBF::N, pybind11::const_))
		.def("N", pybind11::overload_cast<const double, const double>(&InterpolationVectorRBF::N, pybind11::const_))
		.def("gradN", pybind11::overload_cast<const V_d &>(&InterpolationVectorRBF::gradN, pybind11::const_))
		.def("gradN", pybind11::overload_cast<const double, const double>(&InterpolationVectorRBF::gradN, pybind11::const_))
		.def("cross", &InterpolationVectorRBF::cross)
		.def("J", &InterpolationVectorRBF::J);
	/* ------------------------------------------------------ */
	pybind11::class_<Quaternion>(m, "Quaternion")
		.def(pybind11::init<const double, const double, const double, const double>())
		.def(pybind11::init<const T4d &>())
		.def("Rs", pybind11::overload_cast<>(&Quaternion::Rs, pybind11::const_))
		.def("Rs", pybind11::overload_cast<const Tddd &>(&Quaternion::Rs, pybind11::const_))
		.def("Rv", pybind11::overload_cast<>(&Quaternion::Rv, pybind11::const_))
		.def("Rv", pybind11::overload_cast<const Tddd &>(&Quaternion::Rv, pybind11::const_))
		.def("R", pybind11::overload_cast<>(&Quaternion::R, pybind11::const_))
		.def("R", pybind11::overload_cast<const Tddd &>(&Quaternion::R, pybind11::const_))
		.def("__call__", &Quaternion::operator())
		.def("__mul__", [](const Quaternion &A, const Quaternion &B)
			 { return A * B; })
		.def("yaw", &Quaternion::yaw)
		.def("pitch", &Quaternion::pitch)
		.def("roll", &Quaternion::roll)
		.def("YPR", &Quaternion::YPR)
		.def("Ryaw", &Quaternion::Ryaw)
		.def("Rpitch", &Quaternion::Rpitch)
		.def("Rroll", &Quaternion::Rroll)
		.def("set", &Quaternion::set)
		.def("d_dt", &Quaternion::d_dt);
	/* ------------------------------------------------------ */
	pybind11::class_<Histogram>(m, "Histogram")
		.def(pybind11::init<const V_d &>())
		.def_readwrite("data", &Histogram::data)
		.def_readwrite("bins", &Histogram::bins)
		.def_readwrite("interval", &Histogram::interval)
		.def_readwrite("mid_interval", &Histogram::mid_interval)
		.def_readwrite("count", &Histogram::count)
		.def_readwrite("cumulative_count", &Histogram::cumulative_count)
		.def_readwrite("bin_width", &Histogram::bin_width)
		.def_readwrite("diff", &Histogram::diff);
	/* ------------------------------------------------------ */
	pybind11::class_<NewtonRaphson>(m, "NewtonRaphson")
		.def(pybind11::init<const V_d &>())
		.def("update", &NewtonRaphson::update)
		.def_readwrite("X", &NewtonRaphson::X)
		.def_readwrite("dX", &NewtonRaphson::dX);
	/* ------------------------------------------------------ */
	// https://pybind11.readthedocs.io/en/stable/classes.html#overloaded-methods
	// pybind11::const_を忘れない
	pybind11::class_<NetworkObj>(m, "NetworkObj")
		.def(pybind11::init<const std::string &>())
		.def("getPoints", pybind11::overload_cast<>(&NetworkObj::getPoints, pybind11::const_))
		.def("getFaces", &NetworkObj::getFaces)
		.def("getPointIndex", pybind11::overload_cast<const VV_netPp &>(&NetworkObj::getPointIndex, pybind11::const_))
		.def("getPointIndex", pybind11::overload_cast<const V_netPp &>(&NetworkObj::getPointIndex, pybind11::const_))
		.def("getPointIndex", pybind11::overload_cast<const netPp>(&NetworkObj::getPointIndex, pybind11::const_))
		.def("getFaceIndex", pybind11::overload_cast<const VV_netFp &>(&NetworkObj::getFaceIndex, pybind11::const_))
		.def("getFaceIndex", pybind11::overload_cast<const V_netFp &>(&NetworkObj::getFaceIndex, pybind11::const_))
		.def("getFaceIndex", pybind11::overload_cast<const netFp>(&NetworkObj::getFaceIndex, pybind11::const_));

	pybind11::class_<networkPoint>(m, "networkPoint")
		.def(pybind11::init<Network *, Network *, const V_d &>());
	// .def("getNeighborsPolarAsTuple", &networkPoint::getNeighborsPolarAsTuple)
	// .def("getNeighborsPolarAsVariant", &networkPoint::getNeighborsPolarAsVariant);

	pybind11::class_<networkFace>(m, "networkFace")
		.def(pybind11::init<Network *, Network *, const V_netLp &>());
	// .def("getPoints", pybind11::overload_cast<const netPp>(&networkFace::getPoints, pybind11::const_));

	pybind11::class_<networkLine>(m, "networkLine")
		.def(pybind11::init<Network *, netP *, netP *>());

	m.def("extractX", [](const V_netPp &ps)
		  { return extractX(ps); });
	m.def("extractX", [](const V_netFp &fs)
		  { return extractX(fs); });
	m.def("extractPoints", [](const V_netFp &fs)
		  { return extractPoints(fs); });
}
