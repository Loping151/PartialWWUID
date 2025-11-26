from ..wutheringwaves_config import PREFIX

WAVES_CODE_100 = -100
WAVES_CODE_101 = -101
WAVES_CODE_102 = -102
WAVES_CODE_103 = -103
WAVES_CODE_106 = -106
WAVES_CODE_107 = -107
WAVES_CODE_990 = -990
WAVES_CODE_998 = -998
WAVES_CODE_999 = -999

ERROR_CODE = {
    WAVES_CODE_100: "库街区未查询到您的游戏角色，请检查是否对外访问\n",
    WAVES_CODE_101: "请检查token有效性\n",
    WAVES_CODE_102: f"您还未绑定鸣潮token或者您的鸣潮token已失效！\n请使用【{PREFIX}登录】完成绑定！\n",
    WAVES_CODE_103: f"您还未绑定鸣潮特征码, 请使用【{PREFIX}绑定uid】完成绑定！\n",
    WAVES_CODE_106: "您未打开库街区我得资料的对外展示\n",
    WAVES_CODE_107: "您未打开库街区共鸣者列表的对外展示\n",
    WAVES_CODE_990: f"请稍后再试，或者使用【{PREFIX}登录】完成绑定！\n",
    WAVES_CODE_998: "IP可能被封禁，请检查是否存在违规行为\n",
    WAVES_CODE_999: "不知道的错误，先看看日志吧",
}
