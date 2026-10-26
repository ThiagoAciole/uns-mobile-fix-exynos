#include <android/log.h>
#include <android/native_window_jni.h>
#include <jni.h>
#define VK_USE_PLATFORM_ANDROID_KHR
#include <vulkan/vulkan.h>
#include <stdlib.h>

#define TAG "NarutoVulkanProbe"
#define INFO(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define ERROR(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

static void inspect_surface(ANativeWindow *window) {
    const char *extensions[] = { VK_KHR_SURFACE_EXTENSION_NAME, VK_KHR_ANDROID_SURFACE_EXTENSION_NAME };
    VkApplicationInfo application = { .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO, .pApplicationName = "Naruto Vulkan Probe", .apiVersion = VK_API_VERSION_1_0 };
    VkInstanceCreateInfo instance_info = { .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO, .pApplicationInfo = &application, .enabledExtensionCount = 2, .ppEnabledExtensionNames = extensions };
    VkInstance instance = VK_NULL_HANDLE;
    VkResult result = vkCreateInstance(&instance_info, NULL, &instance);
    INFO("vkCreateInstance=%d", result);
    if (result != VK_SUCCESS) return;

    PFN_vkCreateAndroidSurfaceKHR create_surface = (PFN_vkCreateAndroidSurfaceKHR)vkGetInstanceProcAddr(instance, "vkCreateAndroidSurfaceKHR");
    PFN_vkGetPhysicalDeviceSurfaceCapabilitiesKHR get_caps = (PFN_vkGetPhysicalDeviceSurfaceCapabilitiesKHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceCapabilitiesKHR");
    PFN_vkGetPhysicalDeviceSurfaceFormatsKHR get_formats = (PFN_vkGetPhysicalDeviceSurfaceFormatsKHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceFormatsKHR");
    PFN_vkGetPhysicalDeviceSurfaceSupportKHR get_present = (PFN_vkGetPhysicalDeviceSurfaceSupportKHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceSurfaceSupportKHR");
    if (!create_surface || !get_caps || !get_formats || !get_present) {
        ERROR("Missing Vulkan Android surface entry point");
        vkDestroyInstance(instance, NULL);
        return;
    }

    VkAndroidSurfaceCreateInfoKHR surface_info = { .sType = VK_STRUCTURE_TYPE_ANDROID_SURFACE_CREATE_INFO_KHR, .window = window };
    VkSurfaceKHR surface = VK_NULL_HANDLE;
    result = create_surface(instance, &surface_info, NULL, &surface);
    INFO("vkCreateAndroidSurfaceKHR=%d window=%p", result, (void *)window);
    if (result != VK_SUCCESS) {
        vkDestroyInstance(instance, NULL);
        return;
    }

    uint32_t device_count = 0;
    result = vkEnumeratePhysicalDevices(instance, &device_count, NULL);
    INFO("vkEnumeratePhysicalDevices(count)=%d devices=%u", result, device_count);
    VkPhysicalDevice *devices = calloc(device_count ? device_count : 1, sizeof(*devices));
    if (result == VK_SUCCESS && devices) {
        result = vkEnumeratePhysicalDevices(instance, &device_count, devices);
        INFO("vkEnumeratePhysicalDevices(list)=%d devices=%u", result, device_count);
    }

    for (uint32_t d = 0; result == VK_SUCCESS && devices && d < device_count; ++d) {
        VkPhysicalDeviceProperties properties;
        vkGetPhysicalDeviceProperties(devices[d], &properties);
        VkSurfaceCapabilitiesKHR caps;
        VkResult caps_result = get_caps(devices[d], surface, &caps);
        INFO("device[%u]=%s api=%u.%u.%u capsResult=%d", d, properties.deviceName,
             VK_VERSION_MAJOR(properties.apiVersion), VK_VERSION_MINOR(properties.apiVersion),
             VK_VERSION_PATCH(properties.apiVersion), caps_result);
        if (caps_result == VK_SUCCESS) {
            INFO("caps extent=%ux%u min=%ux%u max=%ux%u images=%u..%u transforms=0x%x currentTransform=0x%x alpha=0x%x usage=0x%x gameUsage19Supported=%d",
                 caps.currentExtent.width, caps.currentExtent.height,
                 caps.minImageExtent.width, caps.minImageExtent.height,
                 caps.maxImageExtent.width, caps.maxImageExtent.height,
                 caps.minImageCount, caps.maxImageCount, caps.supportedTransforms,
                 caps.currentTransform, caps.supportedCompositeAlpha, caps.supportedUsageFlags,
                 (caps.supportedUsageFlags & 0x13) == 0x13);
        }

        uint32_t format_count = 0;
        VkResult format_result = get_formats(devices[d], surface, &format_count, NULL);
        VkSurfaceFormatKHR *formats = calloc(format_count ? format_count : 1, sizeof(*formats));
        if (format_result == VK_SUCCESS && formats) format_result = get_formats(devices[d], surface, &format_count, formats);
        INFO("vkGetPhysicalDeviceSurfaceFormatsKHR=%d formats=%u", format_result, format_count);
        VkSurfaceFormatKHR first_format = {0};
        if (format_result == VK_SUCCESS && formats && format_count) first_format = formats[0];
        for (uint32_t i = 0; format_result == VK_SUCCESS && formats && i < format_count; ++i) {
            VkFormatProperties format_properties;
            VkImageFormatProperties image_properties;
            vkGetPhysicalDeviceFormatProperties(devices[d], formats[i].format, &format_properties);
            VkResult image_result = vkGetPhysicalDeviceImageFormatProperties(devices[d], formats[i].format,
                VK_IMAGE_TYPE_2D, VK_IMAGE_TILING_OPTIMAL, 0x13, 0, &image_properties);
            INFO("format[%u]=%d colorSpace=%d optimalFeatures=0x%x colorAttachment=%d imageUsage19Result=%d",
                 i, formats[i].format, formats[i].colorSpace, format_properties.optimalTilingFeatures,
                 (format_properties.optimalTilingFeatures & VK_FORMAT_FEATURE_COLOR_ATTACHMENT_BIT) != 0,
                 image_result);
        }
        free(formats);

        uint32_t queue_count = 0;
        vkGetPhysicalDeviceQueueFamilyProperties(devices[d], &queue_count, NULL);
        VkQueueFamilyProperties *queues = calloc(queue_count ? queue_count : 1, sizeof(*queues));
        if (queues) {
            vkGetPhysicalDeviceQueueFamilyProperties(devices[d], &queue_count, queues);
            for (uint32_t q = 0; q < queue_count; ++q) {
                VkBool32 present = VK_FALSE;
                VkResult present_result = get_present(devices[d], q, surface, &present);
                INFO("queue[%u] flags=0x%x presentResult=%d present=%u", q, queues[q].queueFlags, present_result, present);
                if (caps_result == VK_SUCCESS && format_result == VK_SUCCESS && format_count &&
                    present_result == VK_SUCCESS && present && (queues[q].queueFlags & VK_QUEUE_GRAPHICS_BIT)) {
                    const float priority = 1.0f;
                    VkDeviceQueueCreateInfo queue_info = { .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
                        .queueFamilyIndex = q, .queueCount = 1, .pQueuePriorities = &priority };
                    const char *device_extensions[] = { VK_KHR_SWAPCHAIN_EXTENSION_NAME };
                    VkDeviceCreateInfo device_info = { .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
                        .queueCreateInfoCount = 1, .pQueueCreateInfos = &queue_info,
                        .enabledExtensionCount = 1, .ppEnabledExtensionNames = device_extensions };
                    VkDevice device = VK_NULL_HANDLE;
                    VkResult device_result = vkCreateDevice(devices[d], &device_info, NULL, &device);
                    INFO("vkCreateDevice(graphics+present queue %u)=%d", q, device_result);
                    if (device_result == VK_SUCCESS) {
                        uint32_t image_count = caps.minImageCount + 1;
                        if (caps.maxImageCount && image_count > caps.maxImageCount) image_count = caps.maxImageCount;
                        VkSwapchainCreateInfoKHR swapchain_info = { .sType = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
                            .surface = surface, .minImageCount = image_count, .imageFormat = first_format.format,
                            .imageColorSpace = first_format.colorSpace,
                            .imageExtent = caps.currentExtent, .imageArrayLayers = 1, .imageUsage = 0x13,
                            .imageSharingMode = VK_SHARING_MODE_EXCLUSIVE, .preTransform = VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR,
                            .compositeAlpha = VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR,
                            .presentMode = VK_PRESENT_MODE_FIFO_KHR, .clipped = VK_TRUE };
                        VkSwapchainKHR swapchain = VK_NULL_HANDLE;
                        VkResult swapchain_result = vkCreateSwapchainKHR(device, &swapchain_info, NULL, &swapchain);
                        INFO("vkCreateSwapchainKHR(game parameters)=%d format=%d colorSpace=%d extent=%ux%u images=%u usage=0x%x",
                             swapchain_result, first_format.format, first_format.colorSpace,
                             caps.currentExtent.width, caps.currentExtent.height, image_count, swapchain_info.imageUsage);
                        if (swapchain_result == VK_SUCCESS) vkDestroySwapchainKHR(device, swapchain, NULL);
                        const VkFormat depth_formats[] = { VK_FORMAT_D24_UNORM_S8_UINT, VK_FORMAT_D32_SFLOAT_S8_UINT, VK_FORMAT_D32_SFLOAT };
                        for (uint32_t i = 0; i < sizeof(depth_formats) / sizeof(depth_formats[0]); ++i) {
                            VkFormatProperties depth_properties;
                            vkGetPhysicalDeviceFormatProperties(devices[d], depth_formats[i], &depth_properties);
                            VkImageCreateInfo image_info = { .sType = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO,
                                .imageType = VK_IMAGE_TYPE_2D, .format = depth_formats[i],
                                .extent = { caps.currentExtent.width, caps.currentExtent.height, 1 },
                                .mipLevels = 1, .arrayLayers = 1, .samples = VK_SAMPLE_COUNT_1_BIT,
                                .tiling = (depth_properties.optimalTilingFeatures & VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT)
                                    ? VK_IMAGE_TILING_OPTIMAL : VK_IMAGE_TILING_LINEAR,
                                .usage = 0x27,
                                .sharingMode = VK_SHARING_MODE_EXCLUSIVE,
                                .initialLayout = VK_IMAGE_LAYOUT_UNDEFINED };
                            VkImage image = VK_NULL_HANDLE;
                            VkResult image_result = vkCreateImage(device, &image_info, NULL, &image);
                            INFO("vkCreateImage(engine depth format=%d extent=%ux%u usage=0x%x tiling=%d)=%d",
                                 depth_formats[i], caps.currentExtent.width, caps.currentExtent.height,
                                 image_info.usage, image_info.tiling, image_result);
                            if (image_result == VK_SUCCESS) {
                                VkMemoryRequirements requirements;
                                vkGetImageMemoryRequirements(device, image, &requirements);
                                VkPhysicalDeviceMemoryProperties memory_properties;
                                vkGetPhysicalDeviceMemoryProperties(devices[d], &memory_properties);
                                uint32_t memory_type = memory_properties.memoryTypeCount;
                                for (uint32_t t = 0; t < memory_properties.memoryTypeCount; ++t) {
                                    if ((requirements.memoryTypeBits & (1u << t)) &&
                                        (memory_properties.memoryTypes[t].propertyFlags & VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT)) {
                                        memory_type = t;
                                        break;
                                    }
                                }
                                VkResult allocation_result = VK_ERROR_FEATURE_NOT_PRESENT;
                                VkResult bind_result = VK_ERROR_FEATURE_NOT_PRESENT;
                                VkDeviceMemory memory = VK_NULL_HANDLE;
                                if (memory_type < memory_properties.memoryTypeCount) {
                                    VkMemoryAllocateInfo allocation_info = { .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
                                        .allocationSize = requirements.size, .memoryTypeIndex = memory_type };
                                    allocation_result = vkAllocateMemory(device, &allocation_info, NULL, &memory);
                                    if (allocation_result == VK_SUCCESS)
                                        bind_result = vkBindImageMemory(device, image, memory, 0);
                                }
                                INFO("depth format=%d requirements=%llu memoryBits=0x%x allocate=%d bind=%d",
                                     depth_formats[i], (unsigned long long)requirements.size,
                                     requirements.memoryTypeBits, allocation_result, bind_result);
                                if (bind_result == VK_SUCCESS) {
                                    VkImageViewCreateInfo view_info = { .sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
                                        .image = image, .viewType = VK_IMAGE_VIEW_TYPE_2D, .format = depth_formats[i],
                                        .subresourceRange = { .aspectMask = VK_IMAGE_ASPECT_DEPTH_BIT |
                                            (depth_formats[i] == VK_FORMAT_D32_SFLOAT ? 0 : VK_IMAGE_ASPECT_STENCIL_BIT),
                                            .levelCount = 1, .layerCount = 1 } };
                                    VkImageView view = VK_NULL_HANDLE;
                                    VkResult view_result = vkCreateImageView(device, &view_info, NULL, &view);
                                    INFO("vkCreateImageView(depth format=%d)=%d", depth_formats[i], view_result);
                                    VkAttachmentDescription attachment = { .format = depth_formats[i],
                                        .samples = VK_SAMPLE_COUNT_1_BIT, .loadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE,
                                        .storeOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,
                                        .stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE,
                                        .stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,
                                        .initialLayout = VK_IMAGE_LAYOUT_UNDEFINED,
                                        .finalLayout = VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL };
                                    VkAttachmentReference reference = { .attachment = 0,
                                        .layout = VK_IMAGE_LAYOUT_DEPTH_STENCIL_ATTACHMENT_OPTIMAL };
                                    VkSubpassDescription subpass = { .pipelineBindPoint = VK_PIPELINE_BIND_POINT_GRAPHICS,
                                        .pDepthStencilAttachment = &reference };
                                    VkRenderPassCreateInfo pass_info = { .sType = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
                                        .attachmentCount = 1, .pAttachments = &attachment,
                                        .subpassCount = 1, .pSubpasses = &subpass };
                                    VkRenderPass pass = VK_NULL_HANDLE;
                                    VkResult pass_result = vkCreateRenderPass(device, &pass_info, NULL, &pass);
                                    INFO("vkCreateRenderPass(depth format=%d)=%d", depth_formats[i], pass_result);
                                    if (view_result == VK_SUCCESS && pass_result == VK_SUCCESS) {
                                        VkFramebufferCreateInfo framebuffer_info = { .sType = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
                                            .renderPass = pass, .attachmentCount = 1, .pAttachments = &view,
                                            .width = caps.currentExtent.width, .height = caps.currentExtent.height, .layers = 1 };
                                        VkFramebuffer framebuffer = VK_NULL_HANDLE;
                                        VkResult framebuffer_result = vkCreateFramebuffer(device, &framebuffer_info, NULL, &framebuffer);
                                        INFO("vkCreateFramebuffer(depth format=%d)=%d", depth_formats[i], framebuffer_result);
                                        if (framebuffer_result == VK_SUCCESS) vkDestroyFramebuffer(device, framebuffer, NULL);
                                    }
                                    if (pass_result == VK_SUCCESS) vkDestroyRenderPass(device, pass, NULL);
                                    if (view_result == VK_SUCCESS) vkDestroyImageView(device, view, NULL);
                                }
                                vkDestroyImage(device, image, NULL);
                                if (memory) vkFreeMemory(device, memory, NULL);
                            }
                        }
                        vkDestroyDevice(device, NULL);
                    }
                    break;
                }
            }
            free(queues);
        }

        const VkFormat depth_formats[] = { VK_FORMAT_D24_UNORM_S8_UINT, VK_FORMAT_D32_SFLOAT_S8_UINT, VK_FORMAT_D32_SFLOAT };
        for (uint32_t i = 0; i < sizeof(depth_formats) / sizeof(depth_formats[0]); ++i) {
            VkFormatProperties properties;
            VkImageFormatProperties image_properties;
            vkGetPhysicalDeviceFormatProperties(devices[d], depth_formats[i], &properties);
            VkResult image_result = vkGetPhysicalDeviceImageFormatProperties(devices[d], depth_formats[i],
                VK_IMAGE_TYPE_2D, VK_IMAGE_TILING_OPTIMAL, VK_IMAGE_USAGE_DEPTH_STENCIL_ATTACHMENT_BIT, 0,
                &image_properties);
            INFO("depthFormat[%u]=%d optimalFeatures=0x%x depthAttachment=%d imageResult=%d",
                 i, depth_formats[i], properties.optimalTilingFeatures,
                 (properties.optimalTilingFeatures & VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT) != 0,
                 image_result);
        }
    }

    free(devices);
    vkDestroySurfaceKHR(instance, surface, NULL);
    vkDestroyInstance(instance, NULL);
    INFO("probe complete");
}

JNIEXPORT void JNICALL Java_org_aciolabs_narutovulkanprobe_ProbeActivity_inspect
  (JNIEnv *env, jobject activity, jobject java_surface) {
    ANativeWindow *window = ANativeWindow_fromSurface(env, java_surface);
    INFO("SurfaceView surface=%p", (void *)window);
    if (!window) return;
    inspect_surface(window);
    ANativeWindow_release(window);
}
