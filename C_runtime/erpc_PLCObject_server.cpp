/*
 * Generated by erpcgen 1.11.0 on Wed Mar 27 13:43:44 2024.
 *
 * AUTOGENERATED - DO NOT EDIT
 */


#include "erpc_PLCObject_server.hpp"
#if ERPC_ALLOCATION_POLICY == ERPC_ALLOCATION_POLICY_DYNAMIC
#include <new>
#include "erpc_port.h"
#endif
#include "erpc_manually_constructed.hpp"

#if 11100 != ERPC_VERSION_NUMBER
#error "The generated shim code version is different to the rest of eRPC code."
#endif

using namespace erpc;
using namespace std;
using namespace erpcShim;

#if ERPC_NESTED_CALLS_DETECTION
extern bool nestingDetection;
#endif


//! @brief Function to read struct binary_t
static void read_binary_t_struct(erpc::Codec * codec, binary_t * data);

//! @brief Function to read struct extra_file
static void read_extra_file_struct(erpc::Codec * codec, extra_file * data);

//! @brief Function to read struct list_extra_file_1_t
static void read_list_extra_file_1_t_struct(erpc::Codec * codec, list_extra_file_1_t * data);

//! @brief Function to read struct trace_order
static void read_trace_order_struct(erpc::Codec * codec, trace_order * data);

//! @brief Function to read struct list_trace_order_1_t
static void read_list_trace_order_1_t_struct(erpc::Codec * codec, list_trace_order_1_t * data);


// Read struct binary_t function implementation
static void read_binary_t_struct(erpc::Codec * codec, binary_t * data)
{
    if(NULL == data)
    {
        return;
    }

    uint8_t * data_local;
    codec->readBinary(data->dataLength, &data_local);
    if (data->dataLength > 0)
    {
    data->data = (uint8_t *) erpc_malloc(data->dataLength * sizeof(uint8_t));
        if (data->data == NULL)
        {
            codec->updateStatus(kErpcStatus_MemoryError);
        }
        else
        {
            memcpy(data->data, data_local, data->dataLength);
        }
    }
    else
    {
        data->data = NULL;
    }
}

// Read struct extra_file function implementation
static void read_extra_file_struct(erpc::Codec * codec, extra_file * data)
{
    if(NULL == data)
    {
        return;
    }

    {
        uint32_t fname_len;
        char * fname_local;
        codec->readString(fname_len, &fname_local);
        data->fname = (char*) erpc_malloc((fname_len + 1) * sizeof(char));
        if ((data->fname == NULL) || (fname_local == NULL))
        {
            codec->updateStatus(kErpcStatus_MemoryError);
        }
        else
        {
            memcpy(data->fname, fname_local, fname_len);
            (data->fname)[fname_len] = 0;
        }
    }

    read_binary_t_struct(codec, &(data->blobID));
}

// Read struct list_extra_file_1_t function implementation
static void read_list_extra_file_1_t_struct(erpc::Codec * codec, list_extra_file_1_t * data)
{
    if(NULL == data)
    {
        return;
    }

    codec->startReadList(data->elementsCount);
    data->elements = (extra_file *) erpc_malloc(data->elementsCount * sizeof(extra_file));
    if ((data->elements == NULL) && (data->elementsCount > 0))
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }
    for (uint32_t listCount = 0U; listCount < data->elementsCount; ++listCount)
    {
        read_extra_file_struct(codec, &(data->elements[listCount]));
    }
}

// Read struct trace_order function implementation
static void read_trace_order_struct(erpc::Codec * codec, trace_order * data)
{
    if(NULL == data)
    {
        return;
    }

    codec->read(data->idx);

    read_binary_t_struct(codec, &(data->force));
}

// Read struct list_trace_order_1_t function implementation
static void read_list_trace_order_1_t_struct(erpc::Codec * codec, list_trace_order_1_t * data)
{
    if(NULL == data)
    {
        return;
    }

    codec->startReadList(data->elementsCount);
    data->elements = (trace_order *) erpc_malloc(data->elementsCount * sizeof(trace_order));
    if ((data->elements == NULL) && (data->elementsCount > 0))
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }
    for (uint32_t listCount = 0U; listCount < data->elementsCount; ++listCount)
    {
        read_trace_order_struct(codec, &(data->elements[listCount]));
    }
}


//! @brief Function to write struct binary_t
static void write_binary_t_struct(erpc::Codec * codec, const binary_t * data);

//! @brief Function to write struct log_message
static void write_log_message_struct(erpc::Codec * codec, const log_message * data);

//! @brief Function to write struct PSKID
static void write_PSKID_struct(erpc::Codec * codec, const PSKID * data);

//! @brief Function to write struct PLCstatus
static void write_PLCstatus_struct(erpc::Codec * codec, const PLCstatus * data);

//! @brief Function to write struct trace_sample
static void write_trace_sample_struct(erpc::Codec * codec, const trace_sample * data);

//! @brief Function to write struct TraceVariables
static void write_TraceVariables_struct(erpc::Codec * codec, const TraceVariables * data);

//! @brief Function to write struct list_trace_sample_1_t
static void write_list_trace_sample_1_t_struct(erpc::Codec * codec, const list_trace_sample_1_t * data);


// Write struct binary_t function implementation
static void write_binary_t_struct(erpc::Codec * codec, const binary_t * data)
{
    if(NULL == data)
    {
        return;
    }

    codec->writeBinary(data->dataLength, data->data);
}

// Write struct log_message function implementation
static void write_log_message_struct(erpc::Codec * codec, const log_message * data)
{
    if(NULL == data)
    {
        return;
    }

    {
        uint32_t msg_len = strlen((const char*)data->msg);

        codec->writeString(msg_len, (const char*)data->msg);
    }

    codec->write(data->tick);

    codec->write(data->sec);

    codec->write(data->nsec);
}

// Write struct PSKID function implementation
static void write_PSKID_struct(erpc::Codec * codec, const PSKID * data)
{
    if(NULL == data)
    {
        return;
    }

    {
        uint32_t ID_len = strlen((const char*)data->ID);

        codec->writeString(ID_len, (const char*)data->ID);
    }

    {
        uint32_t PSK_len = strlen((const char*)data->PSK);

        codec->writeString(PSK_len, (const char*)data->PSK);
    }
}

// Write struct PLCstatus function implementation
static void write_PLCstatus_struct(erpc::Codec * codec, const PLCstatus * data)
{
    if(NULL == data)
    {
        return;
    }

    codec->write(static_cast<int32_t>(data->PLCstatus));

    for (uint32_t arrayCount0 = 0U; arrayCount0 < 4U; ++arrayCount0)
    {
        codec->write(data->logcounts[arrayCount0]);
    }
}

// Write struct trace_sample function implementation
static void write_trace_sample_struct(erpc::Codec * codec, const trace_sample * data)
{
    if(NULL == data)
    {
        return;
    }

    codec->write(data->tick);

    write_binary_t_struct(codec, &(data->TraceBuffer));
}

// Write struct TraceVariables function implementation
static void write_TraceVariables_struct(erpc::Codec * codec, const TraceVariables * data)
{
    if(NULL == data)
    {
        return;
    }

    codec->write(static_cast<int32_t>(data->PLCstatus));

    write_list_trace_sample_1_t_struct(codec, &(data->traces));
}

// Write struct list_trace_sample_1_t function implementation
static void write_list_trace_sample_1_t_struct(erpc::Codec * codec, const list_trace_sample_1_t * data)
{
    if(NULL == data)
    {
        return;
    }

    codec->startWriteList(data->elementsCount);
    for (uint32_t listCount = 0U; listCount < data->elementsCount; ++listCount)
    {
        write_trace_sample_struct(codec, &(data->elements[listCount]));
    }
}


//! @brief Function to free space allocated inside struct binary_t
static void free_binary_t_struct(binary_t * data);

//! @brief Function to free space allocated inside struct log_message
static void free_log_message_struct(log_message * data);

//! @brief Function to free space allocated inside struct PSKID
static void free_PSKID_struct(PSKID * data);

//! @brief Function to free space allocated inside struct trace_sample
static void free_trace_sample_struct(trace_sample * data);

//! @brief Function to free space allocated inside struct TraceVariables
static void free_TraceVariables_struct(TraceVariables * data);

//! @brief Function to free space allocated inside struct list_trace_sample_1_t
static void free_list_trace_sample_1_t_struct(list_trace_sample_1_t * data);

//! @brief Function to free space allocated inside struct extra_file
static void free_extra_file_struct(extra_file * data);

//! @brief Function to free space allocated inside struct list_extra_file_1_t
static void free_list_extra_file_1_t_struct(list_extra_file_1_t * data);

//! @brief Function to free space allocated inside struct trace_order
static void free_trace_order_struct(trace_order * data);

//! @brief Function to free space allocated inside struct list_trace_order_1_t
static void free_list_trace_order_1_t_struct(list_trace_order_1_t * data);


// Free space allocated inside struct binary_t function implementation
static void free_binary_t_struct(binary_t * data)
{
    erpc_free(data->data);
}

// Free space allocated inside struct log_message function implementation
static void free_log_message_struct(log_message * data)
{
    erpc_free(data->msg);
}

// Free space allocated inside struct PSKID function implementation
static void free_PSKID_struct(PSKID * data)
{
    erpc_free(data->ID);

    erpc_free(data->PSK);
}

// Free space allocated inside struct trace_sample function implementation
static void free_trace_sample_struct(trace_sample * data)
{
    free_binary_t_struct(&data->TraceBuffer);
}

// Free space allocated inside struct TraceVariables function implementation
static void free_TraceVariables_struct(TraceVariables * data)
{
    free_list_trace_sample_1_t_struct(&data->traces);
}

// Free space allocated inside struct list_trace_sample_1_t function implementation
static void free_list_trace_sample_1_t_struct(list_trace_sample_1_t * data)
{
    for (uint32_t listCount = 0; listCount < data->elementsCount; ++listCount)
    {
        free_trace_sample_struct(&data->elements[listCount]);
    }

    erpc_free(data->elements);
}

// Free space allocated inside struct extra_file function implementation
static void free_extra_file_struct(extra_file * data)
{
    erpc_free(data->fname);

    free_binary_t_struct(&data->blobID);
}

// Free space allocated inside struct list_extra_file_1_t function implementation
static void free_list_extra_file_1_t_struct(list_extra_file_1_t * data)
{
    for (uint32_t listCount = 0; listCount < data->elementsCount; ++listCount)
    {
        free_extra_file_struct(&data->elements[listCount]);
    }

    erpc_free(data->elements);
}

// Free space allocated inside struct trace_order function implementation
static void free_trace_order_struct(trace_order * data)
{
    free_binary_t_struct(&data->force);
}

// Free space allocated inside struct list_trace_order_1_t function implementation
static void free_list_trace_order_1_t_struct(list_trace_order_1_t * data)
{
    for (uint32_t listCount = 0; listCount < data->elementsCount; ++listCount)
    {
        free_trace_order_struct(&data->elements[listCount]);
    }

    erpc_free(data->elements);
}



BeremizPLCObjectService_service::BeremizPLCObjectService_service(BeremizPLCObjectService_interface *_BeremizPLCObjectService_interface)
    : erpc::Service(BeremizPLCObjectService_interface::m_serviceId)
    , m_handler(_BeremizPLCObjectService_interface)
{
}

BeremizPLCObjectService_service::~BeremizPLCObjectService_service()
{
}

// return service interface handler.
BeremizPLCObjectService_interface* BeremizPLCObjectService_service::getHandler(void)
{
    return m_handler;
}

// Call the correct server shim based on method unique ID.
erpc_status_t BeremizPLCObjectService_service::handleInvocation(uint32_t methodId, uint32_t sequence, Codec * codec, MessageBufferFactory *messageFactory, Transport * transport)
{
    erpc_status_t erpcStatus;
    switch (methodId)
    {
        case BeremizPLCObjectService_interface::m_AppendChunkToBlobId:
        {
            erpcStatus = AppendChunkToBlob_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_GetLogMessageId:
        {
            erpcStatus = GetLogMessage_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_GetPLCIDId:
        {
            erpcStatus = GetPLCID_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_GetPLCstatusId:
        {
            erpcStatus = GetPLCstatus_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_GetTraceVariablesId:
        {
            erpcStatus = GetTraceVariables_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_MatchMD5Id:
        {
            erpcStatus = MatchMD5_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_NewPLCId:
        {
            erpcStatus = NewPLC_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_PurgeBlobsId:
        {
            erpcStatus = PurgeBlobs_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_RepairPLCId:
        {
            erpcStatus = RepairPLC_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_ResetLogCountId:
        {
            erpcStatus = ResetLogCount_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_SeedBlobId:
        {
            erpcStatus = SeedBlob_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_SetTraceVariablesListId:
        {
            erpcStatus = SetTraceVariablesList_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_StartPLCId:
        {
            erpcStatus = StartPLC_shim(codec, messageFactory, transport, sequence);
            break;
        }

        case BeremizPLCObjectService_interface::m_StopPLCId:
        {
            erpcStatus = StopPLC_shim(codec, messageFactory, transport, sequence);
            break;
        }

        default:
        {
            erpcStatus = kErpcStatus_InvalidArgument;
            break;
        }
    }

    return erpcStatus;
}

// Server shim for AppendChunkToBlob of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::AppendChunkToBlob_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    binary_t *data = NULL;
    data = (binary_t *) erpc_malloc(sizeof(binary_t));
    if (data == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }
    binary_t *blobID = NULL;
    blobID = (binary_t *) erpc_malloc(sizeof(binary_t));
    if (blobID == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }
    binary_t *newBlobID = NULL;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    read_binary_t_struct(codec, data);

    read_binary_t_struct(codec, blobID);

    newBlobID = (binary_t *) erpc_malloc(sizeof(binary_t));
    if (newBlobID == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->AppendChunkToBlob(data, blobID, newBlobID);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_AppendChunkToBlobId, sequence);

        write_binary_t_struct(codec, newBlobID);

        codec->write(result);

        err = codec->getStatus();
    }

    if (data)
    {
        free_binary_t_struct(data);
    }
    erpc_free(data);

    if (blobID)
    {
        free_binary_t_struct(blobID);
    }
    erpc_free(blobID);

    if (newBlobID)
    {
        free_binary_t_struct(newBlobID);
    }
    erpc_free(newBlobID);

    return err;
}

// Server shim for GetLogMessage of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::GetLogMessage_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    uint8_t level;
    uint32_t msgID;
    log_message *message = NULL;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    codec->read(level);

    codec->read(msgID);

    message = (log_message *) erpc_malloc(sizeof(log_message));
    if (message == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->GetLogMessage(level, msgID, message);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_GetLogMessageId, sequence);

        write_log_message_struct(codec, message);

        codec->write(result);

        err = codec->getStatus();
    }

    if (message)
    {
        free_log_message_struct(message);
    }
    erpc_free(message);

    return err;
}

// Server shim for GetPLCID of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::GetPLCID_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    PSKID *plcID = NULL;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    plcID = (PSKID *) erpc_malloc(sizeof(PSKID));
    if (plcID == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->GetPLCID(plcID);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_GetPLCIDId, sequence);

        write_PSKID_struct(codec, plcID);

        codec->write(result);

        err = codec->getStatus();
    }

    if (plcID)
    {
        free_PSKID_struct(plcID);
    }
    erpc_free(plcID);

    return err;
}

// Server shim for GetPLCstatus of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::GetPLCstatus_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    PLCstatus *status = NULL;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    status = (PLCstatus *) erpc_malloc(sizeof(PLCstatus));
    if (status == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->GetPLCstatus(status);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_GetPLCstatusId, sequence);

        write_PLCstatus_struct(codec, status);

        codec->write(result);

        err = codec->getStatus();
    }

    erpc_free(status);

    return err;
}

// Server shim for GetTraceVariables of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::GetTraceVariables_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    uint32_t debugToken;
    TraceVariables *traces = NULL;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    codec->read(debugToken);

    traces = (TraceVariables *) erpc_malloc(sizeof(TraceVariables));
    if (traces == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->GetTraceVariables(debugToken, traces);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_GetTraceVariablesId, sequence);

        write_TraceVariables_struct(codec, traces);

        codec->write(result);

        err = codec->getStatus();
    }

    if (traces)
    {
        free_TraceVariables_struct(traces);
    }
    erpc_free(traces);

    return err;
}

// Server shim for MatchMD5 of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::MatchMD5_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    char * MD5 = NULL;
    bool match;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    {
        uint32_t MD5_len;
        char * MD5_local;
        codec->readString(MD5_len, &MD5_local);
        MD5 = (char*) erpc_malloc((MD5_len + 1) * sizeof(char));
        if ((MD5 == NULL) || (MD5_local == NULL))
        {
            codec->updateStatus(kErpcStatus_MemoryError);
        }
        else
        {
            memcpy(MD5, MD5_local, MD5_len);
            (MD5)[MD5_len] = 0;
        }
    }

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->MatchMD5(MD5, &match);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_MatchMD5Id, sequence);

        codec->write(match);

        codec->write(result);

        err = codec->getStatus();
    }

    erpc_free(MD5);

    return err;
}

// Server shim for NewPLC of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::NewPLC_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    char * md5sum = NULL;
    binary_t *plcObjectBlobID = NULL;
    plcObjectBlobID = (binary_t *) erpc_malloc(sizeof(binary_t));
    if (plcObjectBlobID == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }
    list_extra_file_1_t *extrafiles = NULL;
    extrafiles = (list_extra_file_1_t *) erpc_malloc(sizeof(list_extra_file_1_t));
    if (extrafiles == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }
    bool success;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    {
        uint32_t md5sum_len;
        char * md5sum_local;
        codec->readString(md5sum_len, &md5sum_local);
        md5sum = (char*) erpc_malloc((md5sum_len + 1) * sizeof(char));
        if ((md5sum == NULL) || (md5sum_local == NULL))
        {
            codec->updateStatus(kErpcStatus_MemoryError);
        }
        else
        {
            memcpy(md5sum, md5sum_local, md5sum_len);
            (md5sum)[md5sum_len] = 0;
        }
    }

    read_binary_t_struct(codec, plcObjectBlobID);

    read_list_extra_file_1_t_struct(codec, extrafiles);

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->NewPLC(md5sum, plcObjectBlobID, extrafiles, &success);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_NewPLCId, sequence);

        codec->write(success);

        codec->write(result);

        err = codec->getStatus();
    }

    erpc_free(md5sum);

    if (plcObjectBlobID)
    {
        free_binary_t_struct(plcObjectBlobID);
    }
    erpc_free(plcObjectBlobID);

    if (extrafiles)
    {
        free_list_extra_file_1_t_struct(extrafiles);
    }
    erpc_free(extrafiles);

    return err;
}

// Server shim for PurgeBlobs of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::PurgeBlobs_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->PurgeBlobs();
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_PurgeBlobsId, sequence);

        codec->write(result);

        err = codec->getStatus();
    }

    return err;
}

// Server shim for RepairPLC of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::RepairPLC_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->RepairPLC();
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_RepairPLCId, sequence);

        codec->write(result);

        err = codec->getStatus();
    }

    return err;
}

// Server shim for ResetLogCount of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::ResetLogCount_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->ResetLogCount();
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_ResetLogCountId, sequence);

        codec->write(result);

        err = codec->getStatus();
    }

    return err;
}

// Server shim for SeedBlob of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::SeedBlob_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    binary_t *seed = NULL;
    seed = (binary_t *) erpc_malloc(sizeof(binary_t));
    if (seed == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }
    binary_t *blobID = NULL;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    read_binary_t_struct(codec, seed);

    blobID = (binary_t *) erpc_malloc(sizeof(binary_t));
    if (blobID == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->SeedBlob(seed, blobID);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_SeedBlobId, sequence);

        write_binary_t_struct(codec, blobID);

        codec->write(result);

        err = codec->getStatus();
    }

    if (seed)
    {
        free_binary_t_struct(seed);
    }
    erpc_free(seed);

    if (blobID)
    {
        free_binary_t_struct(blobID);
    }
    erpc_free(blobID);

    return err;
}

// Server shim for SetTraceVariablesList of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::SetTraceVariablesList_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    list_trace_order_1_t *orders = NULL;
    orders = (list_trace_order_1_t *) erpc_malloc(sizeof(list_trace_order_1_t));
    if (orders == NULL)
    {
        codec->updateStatus(kErpcStatus_MemoryError);
    }
    uint32_t debugtoken;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    read_list_trace_order_1_t_struct(codec, orders);

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->SetTraceVariablesList(orders, &debugtoken);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_SetTraceVariablesListId, sequence);

        codec->write(debugtoken);

        codec->write(result);

        err = codec->getStatus();
    }

    if (orders)
    {
        free_list_trace_order_1_t_struct(orders);
    }
    erpc_free(orders);

    return err;
}

// Server shim for StartPLC of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::StartPLC_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->StartPLC();
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_StartPLCId, sequence);

        codec->write(result);

        err = codec->getStatus();
    }

    return err;
}

// Server shim for StopPLC of BeremizPLCObjectService interface.
erpc_status_t BeremizPLCObjectService_service::StopPLC_shim(Codec * codec, MessageBufferFactory *messageFactory, Transport * transport, uint32_t sequence)
{
    erpc_status_t err = kErpcStatus_Success;

    bool success;
    uint32_t result;

    // startReadMessage() was already called before this shim was invoked.

    err = codec->getStatus();
    if (err == kErpcStatus_Success)
    {
        // Invoke the actual served function.
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = true;
#endif
        result = m_handler->StopPLC(&success);
#if ERPC_NESTED_CALLS_DETECTION
        nestingDetection = false;
#endif

        // preparing MessageBuffer for serializing data
        err = messageFactory->prepareServerBufferForSend(codec->getBufferRef(), transport->reserveHeaderSize());
    }

    if (err == kErpcStatus_Success)
    {
        // preparing codec for serializing data
        codec->reset(transport->reserveHeaderSize());

        // Build response message.
        codec->startWriteMessage(message_type_t::kReplyMessage, BeremizPLCObjectService_interface::m_serviceId, BeremizPLCObjectService_interface::m_StopPLCId, sequence);

        codec->write(success);

        codec->write(result);

        err = codec->getStatus();
    }

    return err;
}
