
#include <stdint.h>
#ifdef _DLLEXPORT
#define WINEXPORT __declspec(dllexport)
#else
#define WINEXPORT __declspec(dllimport)
#endif


typedef enum ERROR_CODE_{
    STATUS_SUCCESS,
    STATUS_ERROR,
    STATUS_SOCKET_FAILED,           //建立SOCKET失败
    STATUS_SOCKET_CONNECT_FAILED,   //连接服务器失败
    STATUS_SOCKET_SEND_FAILED,      //SOCKET发送失败
}ERROR_CODE;



/**
 * @brief 
 *      图像的类型
 */
typedef enum IMG_TYPE_{
    IMG_DEPTH,
    IMG_AMPLITUDE,
    IMG_RGB,
}IMG_TYPE;

/**
 * @brief 
 *      图像数据
 */
typedef struct STRC_IMG_{
    IMG_TYPE type;
    int len;
    uint16_t *data;
}STRC_IMG;

typedef struct STRC_IMG_ALL_{
    STRC_IMG img_rgb;
    STRC_IMG img_amplitude;
    STRC_IMG img_depth;
}STRC_IMG_ALL;


/**
 * @brief
 *      SDK初始化函数
 */
WINEXPORT void api_init();

/**
 * @brief
 *      SDK退出，断开所有连接，清空所有资源。
 */
WINEXPORT void api_exit();


/**
 * @brief
 *      连接到指定ip的设备
 * @param ip
 *      设备IP
 * @param port
 *      设备TCP服务的端口
 * @return int
 *      <0  连接失败
 *      >=0 连接成功，返回对此设备操作的句柄
 */
WINEXPORT int api_connect(char* ip, int port);

/**
 * @brief
 *      断开与设备的连接
 * @param handle
 *      指定的设备句柄
 * @return int
 *      >=0     断开成功
 *      <0      操作失败
 */
WINEXPORT int api_disconnect(int handle);


/**
 * @brief
 *      获取此SDK的版本号
 * @return char*
 *      SDK的版本号
 */
WINEXPORT char* api_get_sdk_ver();

/**
 * @brief
 *      获取指定设备的软件版本号
 * @param handle
 *      指定的设备句柄，由api_connect返回。
 * @return char*
 *      ==NULL  执行失败
 *      !=NULL  设备版本号
 */
WINEXPORT char* api_get_dev_ver(int handle);
/**
 * @brief
 *      获取设备的镜头信息
 * @param handle
 * @return char*
 *      ==NULL  执行失败
 *      !=NULL  镜头信息
 */
WINEXPORT char* api_get_lens_info(int handle);
/**
 * @brief
 *      向指定设备获取图像
 * @param handle
 *      指定设备，由api_connect返回
 * @return STRC_IMG_ALL*
 *      ==NULL     当前无图像数据
 *      !=NULL     返回的图像数据
 *
 */
WINEXPORT STRC_IMG_ALL* api_get_img(int handle);

/**
 * @brief
 *      获取最后一次出错的错误代码
 * @return ERROR_CODE
 */
WINEXPORT ERROR_CODE api_errorcode();
