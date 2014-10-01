__author__ = 'Alimohammad'
import math
import collections
import time
from scipy import stats
import rpyc
from config import Config

class PMV:
    def __init__(self):
        pass

    pmv_list = collections.OrderedDict()
    a = 1
    b = 0
    offset = 0

    @staticmethod
    def add_pmv(pmv_value):
        PMV.pmv_list[time.time()] = pmv_value

    @staticmethod
    def empty_list():
        PMV.pmv_list.clear()

    @staticmethod
    def calculate_ppv(clo, ta, tr, met, vel, rh):
        return PMV.a * PMV.calculate_pmv(clo, ta, tr, met, vel, rh) + PMV.b

    @staticmethod
    def update_parameters():
        parameters = None
        try:
            db_conn = rpyc.connect(Config.service_config["db_service_address"], Config.service_config["db_service_port"])
            try:
                parameters = db_conn.root.get_ppv_parameters(Config.service_config["user_id"])
                db_conn.close()
            except Exception, e:
                Config.logger.warning("There was a problem getting parameters from db")
                Config.logger.error(e)
                db_conn.close()
        except Exception, e:
            Config.logger.warning("There was a problem connecting to db")
            Config.logger.error(e)

        PMV.a = float(parameters["a"])
        PMV.b = float(parameters["b"])
        PMV.offset = float(parameters["offset"])
        Config.logger.info("Parameters updated: [a][%s][b][%s][offset][%s]" % (str(PMV.a), str(PMV.b), str(PMV.offset)))

    @staticmethod
    def calculate_pmv(clo, ta, tr, met, vel, rh):
        fnps = math.exp(16.6536 - 4030.183 / (ta + 235))
        pa = rh * 10 * fnps
        icl = 0.155 * clo
        m = met * 58.15

        fcl = 1.05 + 0.645 * icl
        if icl < 0.078:
            fcl = 1 + 1.29 * icl

        hcf = 12.1 * pow(vel,0.5)
        taa = ta + 273
        tra = tr + 273
        tcla = taa + (35.5 - ta) / (3.5 * (6.45 * icl + 0.1))
        p1 = icl * fcl
        p2 = p1 * 3.96
        p3 = p1 * 100
        p4 = p1 * taa
        p5 = 308.7 - 0.028 * m + p2 * pow((tra / 100),4)
        xn = tcla / 100
        xf = tcla / 50
        eps = 0.000015
        hc = i = 0
        while (i < 1000) and (abs(xn - xf) > eps):
            xf = (xf + xn) / 2
            hcn = 2.38 * pow(abs(100 * xf - taa),0.25)
            if hcf > hcn:
                hc = hcf
            else:
                hc = hcn

            xn = (p5 + p4 * hc - p2 * (pow(xf,4))) / (100 + p3 * hc)
            i += 1
        tcl = 100 * xn - 273
        hl1 = 3.05 * 0.001 * (5733 - 6.99 * m - pa)
        hl2 = 0
        if m > 58.15:
            hl2 = 0.42 * (m - 58.15)

        hl3 = 1.7 * 0.00001 * m * (5867 - pa)
        hl4 = 0.0014 * m * (34 - ta)
        hl5 = 3.96 * fcl * (pow(xn,4) - pow((tra / 100), 4))
        hl6 = fcl * hc * (tcl - ta)
        ts = 0.303 * math.exp(-0.036 * m) + 0.028

        PMVval = ts * (m - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
        return PMVval